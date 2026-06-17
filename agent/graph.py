from langgraph.graph import StateGraph, END
from agent.state import OutreachState
from agent.nodes import (
    load_lead_node,
    research_node,
    persona_node,
    email_writer_node,
    quality_checker_node,
    save_result_node
)


def should_retry(state: OutreachState) -> str:
    """
    Conditional edge function.
    Returns which node to go to next based on quality score.
    """
    if state["quality_score"] < 7 and state["retry_count"] < 2:
        return "retry"
    return "save"


def has_more_leads(state: OutreachState) -> str:
    """
    Conditional edge after saving.
    Loop back if more leads remain, otherwise end.
    """
    if state["current_index"] < len(state["leads"]):
        return "more"
    return "done"


def build_graph():
    graph = StateGraph(OutreachState)

    # Register all nodes
    graph.add_node("load_lead",       load_lead_node)
    graph.add_node("research",        research_node)
    graph.add_node("persona",         persona_node)
    graph.add_node("email_writer",    email_writer_node)
    graph.add_node("quality_checker", quality_checker_node)
    graph.add_node("save_result",     save_result_node)

    # Entry point
    graph.set_entry_point("load_lead")

    # Linear edges
    graph.add_edge("load_lead",    "research")
    graph.add_edge("research",     "persona")
    graph.add_edge("persona",      "email_writer")
    graph.add_edge("email_writer", "quality_checker")

    # Conditional edge — retry or save
    graph.add_conditional_edges(
        "quality_checker",
        should_retry,
        {
            "retry": "email_writer",   # loop back, rewrite email
            "save":  "save_result"     # score good, save it
        }
    )

    # Conditional edge — more leads or end
    graph.add_conditional_edges(
        "save_result",
        has_more_leads,
        {
            "more": "load_lead",   # next lead
            "done": END            # all leads processed
        }
    )

    return graph.compile()


# Compiled graph — import this everywhere
outreach_graph = build_graph()