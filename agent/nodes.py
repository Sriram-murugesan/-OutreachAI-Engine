from langchain_groq import ChatGroq
from tavily import TavilyClient
from dotenv import load_dotenv
from agent.state import OutreachState
from agent.prompts import PERSONA_PROMPT, EMAIL_PROMPT, QUALITY_PROMPT
from db.supabase_client import save_lead, save_email
import os

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def load_lead_node(state: OutreachState) -> OutreachState:
    """Pick the current lead from the list."""
    lead = state["leads"][state["current_index"]]

    # Save lead to Supabase and store the lead_id back
    lead_id = save_lead(
        campaign_id=state["campaign_id"],
        name=lead["name"],
        company=lead["company"],
        linkedin_url=lead["linkedin_url"],
        email=lead.get("email", "")
    )
    lead["lead_id"] = lead_id

    return {
        **state,
        "leads": state["leads"],
        "research": "",
        "persona": "",
        "email_body": "",
        "quality_score": 0,
        "retry_count": 0,
    }


def research_node(state: OutreachState) -> OutreachState:
    """Search the web for info about the current lead."""
    lead = state["leads"][state["current_index"]]

    query = f'{lead["name"]} {lead["company"]} role responsibilities recent news'

    try:
        results = tavily.search(query=query, max_results=3)
        research_text = "\n\n".join([
            r["content"] for r in results["results"]
        ])
    except Exception:
        research_text = f'{lead["name"]} works at {lead["company"]}.'

    return {**state, "research": research_text}


def persona_node(state: OutreachState) -> OutreachState:
    """Build a persona profile from research using the LLM."""
    lead = state["leads"][state["current_index"]]

    prompt = PERSONA_PROMPT.format(
        name=lead["name"],
        company=lead["company"],
        research=state["research"]
    )

    response = llm.invoke(prompt)
    return {**state, "persona": response.content}


def email_writer_node(state: OutreachState) -> OutreachState:
    """Generate a personalized cold email from the persona."""
    prompt = EMAIL_PROMPT.format(persona=state["persona"])
    response = llm.invoke(prompt)
    return {**state, "email_body": response.content}


def quality_checker_node(state: OutreachState) -> OutreachState:
    """Score the email 1-10. If score < 7, signal a retry."""
    prompt = QUALITY_PROMPT.format(email_body=state["email_body"])
    response = llm.invoke(prompt)

    score = 0
    for line in response.content.splitlines():
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except ValueError:
                score = 5

    return {
        **state,
        "quality_score": score,
        "retry_count": state["retry_count"] + 1
    }


def save_result_node(state: OutreachState) -> OutreachState:
    """Save the approved email to Supabase and append to results."""
    lead = state["leads"][state["current_index"]]

    save_email(
        lead_id=lead["lead_id"],
        persona=state["persona"],
        email_body=state["email_body"],
        quality_score=state["quality_score"]
    )

    result = {
        "name": lead["name"],
        "company": lead["company"],
        "linkedin_url": lead["linkedin_url"],
        "email": lead.get("email", ""),
        "lead_id": lead["lead_id"],
        "persona": state["persona"],
        "email_body": state["email_body"],
        "quality_score": state["quality_score"]
    }

    return {
        **state,
        "results": state["results"] + [result],
        "current_index": state["current_index"] + 1
    }