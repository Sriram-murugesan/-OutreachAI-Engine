from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def create_campaign(name: str, user_id: str) -> str:
    """Inserts a new campaign scoped to a user and returns its generated UUID."""
    res = supabase.table("campaigns").insert({
        "name": name,
        "user_id": user_id
    }).execute()
    return res.data[0]["id"]

def get_user_campaigns(user_id: str) -> list:
    """Fetches all campaigns belonging to a specific user, most recent first."""
    res = supabase.table("campaigns").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data

def save_lead(campaign_id: str, name: str, company: str, linkedin_url: str, email: str = "") -> str:
    """Inserts a new lead into the database with optional email support."""
    res = supabase.table("leads").insert({
        "campaign_id": campaign_id,
        "name": name,
        "company": company,
        "linkedin_url": linkedin_url,
        "email": email
    }).execute()
    return res.data[0]["id"]

def save_email(lead_id: str, persona: str, email_body: str, quality_score: int):
    """Saves the generated email variant along with its confidence metrics."""
    supabase.table("emails").insert({
        "lead_id": lead_id,
        "persona": persona,
        "email_body": email_body,
        "quality_score": quality_score,
        "status": "generated"
    }).execute()

def get_email_record(lead_id: str) -> dict:
    """Fetches a saved email record for a given lead to pass to SendGrid."""
    res = supabase.table("emails").select("*").eq("lead_id", lead_id).execute()
    return res.data[0] if res.data else {}