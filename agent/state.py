from typing import TypedDict, List, Optional

class Lead(TypedDict):
    name: str
    company: str
    linkedin_url: str
    email: str  
    lead_id: Optional[str]      # filled after saving to Supabase

class OutreachState(TypedDict):
    campaign_id: str            # Supabase campaign ID
    leads: List[Lead]           # full list from CSV
    current_index: int          # which lead we're processing right now
    research: str               # raw Tavily search output
    persona: str                # synthesized profile by LLM
    email_body: str             # generated cold email
    quality_score: int          # 1-10 score from quality checker
    retry_count: int            # how many times we've looped back
    results: List[dict]         # accumulates finished emails