from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def create_campaign(name: str) -> str:
    res = supabase.table("campaigns").insert({"name": name}).execute()
    return res.data[0]["id"]

def save_lead(campaign_id: str, name: str, company: str, linkedin_url: str) -> str:
    res = supabase.table("leads").insert({
        "campaign_id": campaign_id,
        "name": name,
        "company": company,
        "linkedin_url": linkedin_url
    }).execute()
    return res.data[0]["id"]

def save_email(lead_id: str, persona: str, email_body: str, quality_score: int):
    supabase.table("emails").insert({
        "lead_id": lead_id,
        "persona": persona,
        "email_body": email_body,
        "quality_score": quality_score,
        "status": "generated"
    }).execute()