from langgraph.graph import StateGraph, END
from feature2.state import Feature2State
from feature2.nodes import (
    fetch_jd_node,
    fetch_candidates_node,
    embedding_node,
    ranking_node,
    shortlist_node,
)


def create_feature2_graph(checkpointer=None):
    """Create and compile the Feature 2 LangGraph workflow."""

    workflow = StateGraph(Feature2State)

    workflow.add_node("fetch_jd", fetch_jd_node)
    workflow.add_node("fetch_candidates", fetch_candidates_node)
    workflow.add_node("embedding", embedding_node)
    workflow.add_node("ranking", ranking_node)
    workflow.add_node("shortlist", shortlist_node)

    workflow.set_entry_point("fetch_jd")

    workflow.add_edge("fetch_jd", "fetch_candidates")
    workflow.add_edge("fetch_candidates", "embedding")
    workflow.add_edge("embedding", "ranking")
    workflow.add_edge("ranking", "shortlist")
    workflow.add_edge("shortlist", END)

    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()
