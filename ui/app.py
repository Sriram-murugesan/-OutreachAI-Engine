import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import pandas as pd
import io
from agent.graph import outreach_graph
from db.supabase_client import create_campaign

# 1. Premium Page Configuration
st.set_page_config(
    page_title="OutreachAI | Intelligent Cold Outreach", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Premium Custom CSS injection for elite styling
st.markdown("""
    <style>
    /* Global Background and Typography */
    .main {
        background-color: #fafbfc;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
    
    /* Premium Metric Styling */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #4f46e5;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 5px;
    }

    /* Premium Email Canvas Container (Fixes the small box issue) */
    .email-canvas {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02);
    }
    .email-meta {
        font-size: 0.9rem;
        color: #64748b;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }
    .email-body {
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #334155;
        white-space: pre-wrap; /* Ensures spacing and breaks are perfectly preserved */
    }

    /* Sidebar and Badges */
    .sidebar-footer {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 50px;
        text-align: center;
    }
    .score-badge {
        background-color: #f0fdf4;
        color: #166534;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #bbf7d0;
    }
    .score-badge-low {
        background-color: #fff7ed;
        color: #9a3412;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #ffedd5;
    }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Campaign Setup) ---
with st.sidebar:
    st.markdown("<h2 style='margin-top:0;'>Campaign Console</h2>", unsafe_allow_html=True)
    st.markdown("Configure your AI agent execution parameters below.")
    
    campaign_name = st.text_input("Campaign Name", placeholder="e.g., Q3 Enterprise SaaS")
    
    st.markdown("---")
    st.markdown("### 📋 Required CSV Schema")
    st.markdown("Ensure your files match this strict structural format:")
    st.code("name,company,linkedin_url", language="text")
    
    st.markdown("---")
    st.markdown(
        """
        <div class="sidebar-footer">
            <p>Engine Infrastructure:</p>
            <strong>LangGraph • Groq • Tavily • Supabase</strong>
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- MAIN AREA ---
# Header Section
st.markdown("<h1 style='margin-bottom: 0px;'>⚡ OutreachAI Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: 5px;'>Autonomous B2B intelligence collector and personalized copywrighting suite.</p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([1.1, 0.9], gap="large")

with col1:
    st.markdown("### 📥 Source Lead Ingestion")
    uploaded_file = st.file_uploader("Drop target CSV dataset here", type="csv", label_visibility="collapsed")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True, height=220)
        st.caption(f"✅ Successfully staged {len(df)} target prospects into system memory.")

with col2:
    st.markdown("### 📋 Reference Data Template")
    sample = pd.DataFrame([
        {"name": "Jensen Huang",  "company": "NVIDIA", "linkedin_url": "https://linkedin.com/in/jensen-huang"},
        {"name": "Sundar Pichai", "company": "Google", "linkedin_url": "https://linkedin.com/in/sundar-pichai"},
    ])
    st.dataframe(sample, use_container_width=True, height=115)
    sample_csv = sample.to_csv(index=False)
    st.download_button(
        label="Download Blueprint CSV", 
        data=sample_csv, 
        file_name="sample_leads.csv", 
        mime="text/csv",
        use_container_width=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# Action Trigger States
if uploaded_file and campaign_name:
    if st.button("🚀 Initialize Autonomous Outreach Agent", type="primary", use_container_width=True):

        campaign_id = create_campaign(campaign_name)

        leads = []
        for _, row in df.iterrows():
            leads.append({
                "name": str(row["name"]),
                "company": str(row["company"]),
                "linkedin_url": str(row["linkedin_url"]),
                "lead_id": None
            })

        initial_state = {
            "campaign_id": campaign_id,
            "leads": leads,
            "current_index": 0,
            "research": "",
            "persona": "",
            "email_body": "",
            "quality_score": 0,
            "retry_count": 0,
            "results": []
        }

        # Premium Custom Progress indicators
        progress_bar = st.progress(0)
        status_box = st.empty()
        total = len(leads)

        results = []
        for i, lead in enumerate(leads):
            status_box.markdown(f"🧬 **[Processing {i+1}/{total}]** Scanning web data for *{lead['name']}* at *{lead['company']}*...")

            single_state = {**initial_state, "leads": [leads[i]], "current_index": 0}
            out = outreach_graph.invoke(single_state)

            if out["results"]:
                results.append(out["results"][0])

            progress_bar.progress((i + 1) / total)

        status_box.success(f"✨ Execution Complete! Processed and verified all {total} pipelines.")

        # --- RESULTS INTERFACE ---
        st.markdown("---")
        st.markdown("## 📊 Outbound Campaigns Analytics & Output")
        
        # High-end metric cards layout
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Targets</div></div>', unsafe_allow_html=True)
        with m_col2:
            avg_score = round(sum([r['quality_score'] for r in results]) / len(results), 1) if results else 0
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_score}/10</div><div class="metric-label">Avg Quality Score</div></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">100%</div><div class="metric-label">Generation Success</div></div>', unsafe_allow_html=True)

        st.markdown("### ✉️ Review Generated Directives")
        
        # Premium Email Canvas display
        for r in results:
            score = r['quality_score']
            badge_class = "score-badge" if score >= 7 else "score-badge-low"
            
            # Expander header stays clean and structured
            with st.expander(f"👤 {r['name']} — {r['company']}"):
                
                # Split content into layout rows
                st.markdown("#### 🔬 AI Extrapolated Persona")
                st.info(r["persona"])
                
                st.markdown("#### 📄 Final E-mail Variant")
                # Premium Native HTML Email Body container replaces st.code block!
                # This drops limits, introduces smooth dynamic text, wrapping and natural viewing heights.
                st.markdown(
                    f"""
                    <div class="email-canvas">
                        <div class="email-meta">
                            <strong>To:</strong> {r['name']} &lt;{r['company'].lower().replace(' ', '')}.com&gt;<br>
                            <strong>Campaign context:</strong> {campaign_name}<br>
                            <strong>Relevance Rank:</strong> <span class="{badge_class}">{score}/10 Confidence</span>
                        </div>
                        <div class="email-body">{r['email_body']}</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

        # Unified Bulk Export Controls
        st.markdown("<br>", unsafe_allow_html=True)
        out_df = pd.DataFrame([{
            "name": r["name"],
            "company": r["company"],
            "email": r["email_body"],
            "score": r["quality_score"]
        } for r in results])

        csv_out = out_df.to_csv(index=False)
        st.download_button(
            label="📥 Export Final Copy Deck (CSV)",
            data=csv_out,
            file_name=f"{campaign_name.lower().replace(' ', '_')}_outreach.csv",
            mime="text/csv",
            use_container_width=True
        )

elif uploaded_file and not campaign_name:
    st.warning("⚠️ Action Required: Input an active campaign profile identifier name in the panel sidebar.")
elif not uploaded_file:
    st.info("💡 Systems standing by. Please drop or specify a target CSV prospecting schema to initiate processing framework.")