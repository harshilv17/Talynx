from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from feature1.state import Feature1State
from feature1.nodes import validate_node, jd_generation_node, guardrail_node, review_node, publish_node
from sqlalchemy.orm import Session


def should_continue_after_validation(state: Feature1State) -> str:
    """Route after validation."""
    if state.get("validation_errors"):
        return "end"
    return "jd_generation"


def should_continue_after_review(state: Feature1State) -> str:
    """Route after human review."""
    decision = state.get("review_decision")
    
    if decision == "approve":
        return "publish"
    
    elif decision == "edit":
        return "publish"
    
    elif decision == "revise":
        revision_count = state.get("revision_count", 0)
        if revision_count >= 3:
            return "end"
        return "jd_generation"
    
    return "review"


def create_feature1_graph(db: Session, checkpointer: PostgresSaver = None):
    """Create and compile the Feature 1 LangGraph workflow."""
    
    workflow = StateGraph(Feature1State)
    
    workflow.add_node("validate", lambda state: validate_node(state, db))
    workflow.add_node("jd_generation", lambda state: jd_generation_node(state, db))
    workflow.add_node("guardrail", lambda state: guardrail_node(state, db))
    workflow.add_node("review", review_node)
    workflow.add_node("publish", lambda state: publish_node(state, db))
    
    workflow.set_entry_point("validate")
    
    workflow.add_conditional_edges(
        "validate",
        should_continue_after_validation,
        {
            "jd_generation": "jd_generation",
            "end": END
        }
    )
    
    workflow.add_edge("jd_generation", "guardrail")
    workflow.add_edge("guardrail", "review")
    
    workflow.add_conditional_edges(
        "review",
        should_continue_after_review,
        {
            "publish": "publish",
            "jd_generation": "jd_generation",
            "review": "review",
            "end": END
        }
    )
    
    workflow.add_edge("publish", END)
    
    if checkpointer:
        return workflow.compile(checkpointer=checkpointer)
    return workflow.compile()
