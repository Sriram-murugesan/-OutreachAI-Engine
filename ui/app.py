import sys
import os
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root not in sys.path:
    sys.path.insert(0, root)

import streamlit as st
import pandas as pd
from agent.graph import outreach_graph
from db.supabase_client import create_campaign, get_email_record
from db.email_sender import send_email

st.set_page_config(page_title="Cold Outreach Agent", page_icon="📧", layout="wide")

st.title("Cold Outreach Agent")
st.caption("Upload leads → AI generates personalized emails → send with one click")

with st.sidebar:
    st.header("Campaign setup")
    campaign_name = st.text_input("Campaign name", placeholder="Q1 SaaS Outreach")
    st.markdown("---")
    st.markdown("**CSV format required:**")
    st.code("name,company,linkedin_url,email", language="text")
    st.markdown("---")
    st.caption("Stack: LangGraph + Groq + Tavily + Supabase + SendGrid")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload leads")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df, use_container_width=True)
        st.caption(f"{len(df)} leads loaded")

with col2:
    st.subheader("Sample CSV")
    sample = pd.DataFrame([
        {"name": "Jensen Huang",  "company": "NVIDIA", "linkedin_url": "https://linkedin.com/in/jensen-huang", "email": "jensen@nvidia.com"},
        {"name": "Sundar Pichai", "company": "Google", "linkedin_url": "https://linkedin.com/in/sundar-pichai", "email": "sundar@google.com"},
    ])
    st.dataframe(sample, use_container_width=True)
    st.download_button("Download sample CSV", sample.to_csv(index=False), "sample_leads.csv", "text/csv")

st.markdown("---")

if uploaded_file and campaign_name:
    if st.button("Generate emails", type="primary", use_container_width=True):

        campaign_id = create_campaign(campaign_name)
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

        progress = st.progress(0, text="Starting agent...")
        status = st.empty()
        total = len(leads)
        results = []

        for i, lead in enumerate(leads):
            status.info(f"Processing {lead['name']} @ {lead['company']}...")
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
            progress.progress((i + 1) / total, text=f"Done {i+1}/{total} leads")

        status.success(f"All {total} emails generated!")
        st.session_state["results"] = results

# Show results if they exist in session
if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]

    st.subheader("Generated emails")

    for i, r in enumerate(results):
        with st.expander(f"{r['name']} @ {r['company']}  —  Score: {r['quality_score']}/10"):
            st.markdown("**Persona**")
            st.write(r["persona"])
            st.markdown("**Email**")
            st.code(r["email_body"], language="text")

            # Send button per email
            col_send, col_status = st.columns([1, 2])
            with col_send:
                if st.button(f"Send to {r.get('email', 'N/A')}", key=f"send_{i}"):
                    if not r.get("email"):
                        st.error("No email address for this lead.")
                    else:
                        # Fetch email record ID from Supabase
                        record = get_email_record(r["lead_id"])
                        if record:
                            success = send_email(
                                to_email=r["email"],
                                subject="",
                                body=r["email_body"],
                                email_id=record["id"]
                            )
                            if success:
                                st.success("Sent!")
                            else:
                                st.error("Failed to send. Check SendGrid config.")
                        else:
                            st.error("Email record not found in DB.")

    # Download CSV
    out_df = pd.DataFrame([{
        "name": r["name"],
        "company": r["company"],
        "email": r.get("email", ""),
        "email_body": r["email_body"],
        "score": r["quality_score"]
    } for r in results])

    st.download_button(
        "Download emails CSV",
        out_df.to_csv(index=False),
        "outreach_emails.csv",
        "text/csv",
        use_container_width=True
    )

elif not uploaded_file:
    st.info("Upload a CSV file to get started.")