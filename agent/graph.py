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
    if state["quality_score"] < 7 and state["retry_count"] < 2:
        return "retry"
    return "save"


def has_more_leads(state: OutreachState) -> str:
    if state["current_index"] < len(state["leads"]):
        return "more"
    return "done"


def build_graph():
    graph = StateGraph(OutreachState)

    # Register nodes — names must match exactly below
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

    # Conditional: retry or save
    graph.add_conditional_edges(
        "quality_checker",
        should_retry,
        {
            "retry": "email_writer",
            "save":  "save_result"
        }
    )

    # Conditional: more leads or end
    graph.add_conditional_edges(
        "save_result",
        has_more_leads,
        {
            "more": "load_lead",
            "done": END
        }
    )

    return graph.compile()


outreach_graph = build_graph()