import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

import streamlit as st
import pandas as pd
from agent.graph import outreach_graph
from db.supabase_client import (
    create_campaign,
    get_email_record,
    get_user_campaigns,
    get_campaign_leads_and_emails,
    get_user_stats
)
from db.email_sender import send_email
from auth.auth_handler import sign_up, sign_in, sign_out

# 1. Premium Page Configuration
st.set_page_config(
    page_title="OutreachAI Express | Intelligent Delivery",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Premium Custom CSS injection for elite styling
st.markdown("""
    <style>
    .main {
        background-color: #fafbfc;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
        color: #1e293b !important;
    }
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
    .email-canvas {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 20px;
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
        white-space: pre-wrap;
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
    .sidebar-footer {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 50px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- AUTH GATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<h1 style='text-align:center;'>⚡ OutreachAI Express</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#64748b;'>Log in to access your campaigns</p>",
        unsafe_allow_html=True
    )

    _, center_col, _ = st.columns([1, 1.2, 1])
    with center_col:
        tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

        with tab_login:
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            if st.button("Log in", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Enter both email and password.")
                else:
                    success, result = sign_in(login_email, login_password)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = result
                        st.session_state["user_email"] = login_email
                        st.rerun()
                    else:
                        st.error(result)

        with tab_signup:
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            if st.button("Create account", type="primary", use_container_width=True):
                if not signup_email or not signup_password:
                    st.error("Enter both email and password.")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    success, message = sign_up(signup_email, signup_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)

    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"Logged in as **{st.session_state.get('user_email', '')}**")
    if st.button("Log out", use_container_width=True):
        sign_out()
        st.session_state["authenticated"] = False
        st.session_state.pop("user_id", None)
        st.session_state.pop("user_email", None)
        st.rerun()

    st.markdown("---")

    page = st.radio("Navigate", ["New campaign", "Past campaigns"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<h2 style='margin-top:0;'>Campaign Console</h2>", unsafe_allow_html=True)
    st.markdown("Configure your AI agent and transmission setup below.")

    campaign_name = st.text_input("Campaign name", placeholder="e.g., Q1 SaaS Outreach")

    st.markdown("---")
    st.markdown("### 📋 Required CSV Schema")
    st.markdown("Ensure your files match this structure:")
    st.code("name,company,linkedin_url,email", language="text")

    st.markdown("---")
    st.markdown(
        """
        <div class="sidebar-footer">
            <p>Delivery Infrastructure:</p>
            <strong>LangGraph • Groq • Tavily • Supabase • SendGrid</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PAGE: NEW CAMPAIGN
# =========================================================
if page == "New campaign":

    st.markdown("<h1 style='margin-bottom: 0px;'>⚡ OutreachAI Express</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #64748b; font-size: 1.1rem; margin-top: 5px;'>Autonomous B2B intelligence research linked with an integrated transactional email dispatch engine.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        st.markdown("### 📥 Source Lead Ingestion")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", label_visibility="collapsed")
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df, use_container_width=True, height=220)
            st.caption(f"✅ Successfully staged {len(df)} target prospects into runtime queue.")

    with col2:
        st.markdown("### 📋 Reference Data Template")
        sample = pd.DataFrame([
            {"name": "Jensen Huang",  "company": "NVIDIA", "linkedin_url": "https://linkedin.com/in/jensen-huang", "email": "jensen@nvidia.com"},
            {"name": "Sundar Pichai", "company": "Google", "linkedin_url": "https://linkedin.com/in/sundar-pichai", "email": "sundar@google.com"},
        ])
        st.dataframe(sample, use_container_width=True, height=115)
        st.download_button(
            label="Download Blueprint CSV",
            data=sample.to_csv(index=False),
            file_name="sample_leads.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if uploaded_file and campaign_name:
        if st.button("🚀 Initialize and Generate Campaign Emails", type="primary", use_container_width=True):

            campaign_id = create_campaign(campaign_name, st.session_state["user_id"])
            st.session_state["campaign_id"] = campaign_id

            leads = []
            for _, row in df.iterrows():
                leads.append({
                    "name": str(row["name"]),
                    "company": str(row["company"]),
                    "linkedin_url": str(row.get("linkedin_url", "")),
                    "email": str(row.get("email", "")),
                    "lead_id": None
                })

            progress_bar = st.progress(0)
            status_box = st.empty()
            total = len(leads)
            results = []

            for i, lead in enumerate(leads):
                status_box.markdown(f"🧬 **[Processing {i+1}/{total}]** Scanning data for *{lead['name']}* at *{lead['company']}*...")
                single_state = {
                    "campaign_id": campaign_id,
                    "leads": [lead],
                    "current_index": 0,
                    "research": "",
                    "persona": "",
                    "email_body": "",
                    "quality_score": 0,
                    "retry_count": 0,
                    "results": []
                }
                out = outreach_graph.invoke(single_state)
                if out["results"]:
                    results.append(out["results"][0])
                progress_bar.progress((i + 1) / total)

            status_box.success(f"✨ Execution Complete! Processed and compiled all {total} emails.")
            st.session_state["results"] = results

    if "results" in st.session_state and st.session_state["results"]:
        results = st.session_state["results"]

        st.markdown("---")
        st.markdown("## 📊 Outbound Analytics & Directives")

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(results)}</div><div class="metric-label">Total Leads Generated</div></div>', unsafe_allow_html=True)
        with m_col2:
            avg_score = round(sum([r['quality_score'] for r in results]) / len(results), 1) if results else 0
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_score}/10</div><div class="metric-label">Average Copy Rank</div></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">SendGrid</div><div class="metric-label">Active Gateway Router</div></div>', unsafe_allow_html=True)

        st.markdown("### ✉️ Review & Send Directives")

        for i, r in enumerate(results):
            score = r['quality_score']
            badge_class = "score-badge" if score >= 7 else "score-badge-low"

            with st.expander(f"👤 {r['name']} — {r['company']}"):
                st.markdown("#### 🔬 AI Extrapolated Persona")
                st.info(r["persona"])

                st.markdown("#### 📄 Final E-mail Variant")
                st.markdown(
                    f"""
                    <div class="email-canvas">
                        <div class="email-meta">
                            <strong>To:</strong> {r['name']} &lt;{r.get('email', 'N/A')}&gt;<br>
                            <strong>Campaign Context:</strong> {campaign_name}<br>
                            <strong>System Alignment Rank:</strong> <span class="{badge_class}">{score}/10 Confidence</span>
                        </div>
                        <div class="email-body">{r['email_body']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                col_send, col_status = st.columns([1.2, 2.3])
                with col_send:
                    if st.button(f"📤 Dispatch Mail to {r.get('email', 'N/A')}", key=f"send_{i}", use_container_width=True):
                        if not r.get("email"):
                            st.error("No email address for this lead.")
                        else:
                            record = get_email_record(r["lead_id"])
                            if record:
                                success, error_msg = send_email(
                                    to_email=r["email"],
                                    subject="",
                                    body=r["email_body"],
                                    email_id=record["id"]
                                )
                                if success:
                                    st.success("🚀 Dispatched Successfully!")
                                else:
                                    st.error(f"Failed to send: {error_msg}")
                            else:
                                st.error("⚠️ Record verification missing inside DB system indexes.")

        st.markdown("<br>", unsafe_allow_html=True)
        out_df = pd.DataFrame([{
            "name": r["name"],
            "company": r["company"],
            "email": r.get("email", ""),
            "email_body": r["email_body"],
            "score": r["quality_score"]
        } for r in results])

        st.download_button(
            label="📥 Export Campaign Output Logs (CSV)",
            data=out_df.to_csv(index=False),
            file_name=f"{campaign_name.lower().replace(' ', '_')}_outreach_delivery.csv",
            mime="text/csv",
            use_container_width=True
        )

    elif uploaded_file and not campaign_name:
        st.warning("⚠️ Action Required: Input an active campaign profile identifier name in the panel sidebar.")
    elif not uploaded_file:
        st.info("💡 Systems standing by. Please drop or specify a target CSV prospecting schema to initiate processing framework.")

# =========================================================
# PAGE: PAST CAMPAIGNS
# =========================================================
elif page == "Past campaigns":

    st.markdown("<h1 style='margin-bottom: 0px;'>📊 Past campaigns</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #64748b; font-size: 1.1rem; margin-top: 5px;'>Review and revisit your campaign history</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    stats = get_user_stats(st.session_state["user_id"])

    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total_campaigns"]}</div><div class="metric-label">Total campaigns</div></div>', unsafe_allow_html=True)
    with s_col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["total_emails"]}</div><div class="metric-label">Emails generated</div></div>', unsafe_allow_html=True)
    with s_col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{stats["avg_score"]}/10</div><div class="metric-label">Avg quality score</div></div>', unsafe_allow_html=True)

    st.markdown("### Campaign history")

    campaigns = get_user_campaigns(st.session_state["user_id"])

    if not campaigns:
        st.info("No campaigns yet. Create one from the 'New campaign' tab.")
    else:
        for c in campaigns:
            created_date = c["created_at"][:10] if c.get("created_at") else "unknown"
            with st.expander(f"📁 {c['name']}  —  {created_date}"):
                leads_data = get_campaign_leads_and_emails(c["id"])

                if not leads_data:
                    st.caption("No leads found for this campaign.")
                    continue

                for ld in leads_data:
                    score = ld["quality_score"]
                    badge_class = "score-badge" if score >= 7 else "score-badge-low"

                    st.markdown(
                        f"""
                        <div class="email-canvas">
                            <div class="email-meta">
                                <strong>{ld['name']}</strong> — {ld['company']}<br>
                                <strong>Email:</strong> {ld.get('email', 'N/A')}<br>
                                <span class="{badge_class}">{score}/10</span>
                                &nbsp; <span style="color:#64748b;">Status: {ld['status']}</span>
                            </div>
                            <div class="email-body">{ld['email_body']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )