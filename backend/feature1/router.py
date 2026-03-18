from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid

from feature1.schemas import (
    RoleBriefInput, StartJobResponse, StatusResponse,
    ReviewDecisionInput, ReviewDecisionResponse, PublishedJDResponse,
    JDContent, GuardrailResult, GuardrailIssue,
)
from feature1.models import RoleBriefStatus, JDStatus
from feature1.state import Feature1State
from feature1.graph import create_feature1_graph
from feature1.checkpointer import get_checkpointer
from feature1 import db_ops

router = APIRouter(prefix="/api/v1/feature1", tags=["feature1"])

# ─────────────────────────────────────────────
# Background task helpers
# ─────────────────────────────────────────────

def _get_channel_values(checkpoint):
    """Extract channel_values from checkpoint (supports both Checkpoint and CheckpointTuple)."""
    if hasattr(checkpoint, "channel_values"):
        return checkpoint.channel_values
    if hasattr(checkpoint, "checkpoint") and hasattr(checkpoint.checkpoint, "channel_values"):
        return checkpoint.checkpoint.channel_values
    return None


def run_graph_background(thread_id: str, initial_state: Feature1State):
    """Start the graph from scratch in a background thread."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        with get_checkpointer() as cp:
            graph = create_feature1_graph(cp)
            graph.invoke(initial_state, config)
    except Exception as e:
        db_ops.update_role_brief_status(thread_id, RoleBriefStatus.FAILED, str(e))


def resume_graph_background(thread_id: str, decision_state: dict):
    """Resume a paused (interrupted) graph with a review decision."""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        with get_checkpointer() as cp:
            graph = create_feature1_graph(cp)
            checkpoint = cp.get(config)
            if checkpoint:
                channel_values = _get_channel_values(checkpoint)
                if channel_values is not None:
                    current = dict(channel_values)
                    current.update(decision_state)
                    graph.invoke(current, config)
    except Exception as e:
        db_ops.update_role_brief_status(thread_id, RoleBriefStatus.FAILED, str(e))


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.post("/start", response_model=StartJobResponse)
def start_job_generation(
    role_brief_input: RoleBriefInput,
    background_tasks: BackgroundTasks,
):
    """Submit a role brief, immediately return a thread_id and kick off generation."""
    thread_id = str(uuid.uuid4())
    role_brief_data = role_brief_input.model_dump(mode="json")

    db_ops.create_role_brief(thread_id, role_brief_data)

    initial_state: Feature1State = {
        "thread_id": thread_id,
        "role_brief": role_brief_data,
        "validation_errors": None,
        "jd_draft": None,
        "guardrail_result": None,
        "review_decision": None,
        "edited_jd": None,
        "feedback": None,
        "version": 1,
        "revision_count": 0,
        "status": "validating",
        "error_message": None,
    }

    background_tasks.add_task(run_graph_background, thread_id, initial_state)
    return StartJobResponse(thread_id=thread_id, status="validating")


@router.get("/status/{thread_id}", response_model=StatusResponse)
def get_status(thread_id: str):
    """Return the current state of the graph for a given thread."""
    brief = db_ops.get_role_brief_by_thread(thread_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Thread not found")

    brief_status = brief.get("status", RoleBriefStatus.PENDING)
    if isinstance(brief_status, str):
        pass
    else:
        brief_status = brief_status.value if hasattr(brief_status, "value") else str(brief_status)

    config = {"configurable": {"thread_id": thread_id}}

    try:
        with get_checkpointer() as cp:
            checkpoint = cp.get(config)

        channel_values = _get_channel_values(checkpoint) if checkpoint else None
        if channel_values:
            state = channel_values

            jd_draft = None
            raw_jd = state.get("jd_draft")
            if raw_jd:
                jd_draft = JDContent(**(raw_jd if isinstance(raw_jd, dict) else raw_jd))

            guardrail_result = None
            raw_gr = state.get("guardrail_result")
            if raw_gr:
                guardrail_result = GuardrailResult(**(raw_gr if isinstance(raw_gr, dict) else raw_gr))

            return StatusResponse(
                thread_id=thread_id,
                status=state.get("status", brief_status),
                role_brief=None,
                jd_draft=jd_draft,
                guardrail_result=guardrail_result,
                version=state.get("version", 1),
                error_message=state.get("error_message") or brief.get("error_message"),
            )
    except Exception:
        pass

    # Fallback: when pending_review or checkpoint missing jd, use database
    # Also handle PUBLISHED - once publish_node updates DB, return immediately (fixes "stuck" publish)
    if brief_status == RoleBriefStatus.PUBLISHED:
        jd_rec = db_ops.get_job_description_by_thread_status(thread_id, JDStatus.PUBLISHED)
        if jd_rec:
            return StatusResponse(
                thread_id=thread_id,
                status="published",
                jd_draft=JDContent(**jd_rec["jd_content"]),
                guardrail_result=GuardrailResult(
                    passed=bool(jd_rec.get("guardrail_passed")),
                    issues=[GuardrailIssue(**i) for i in (jd_rec.get("guardrail_issues") or [])],
                    corrected_jd=None,
                    tone_score=jd_rec.get("tone_score") or 0.0,
                ),
                version=jd_rec.get("version", 1),
                error_message=brief.get("error_message"),
            )

    if brief_status == RoleBriefStatus.PENDING_REVIEW:
        jd_rec = db_ops.get_job_description_by_thread_status(thread_id, JDStatus.PENDING_REVIEW)
        if jd_rec:
            return StatusResponse(
                thread_id=thread_id,
                status=brief_status,
                jd_draft=JDContent(**jd_rec["jd_content"]),
                guardrail_result=GuardrailResult(
                    passed=bool(jd_rec.get("guardrail_passed")),
                    issues=[GuardrailIssue(**i) for i in (jd_rec.get("guardrail_issues") or [])],
                    corrected_jd=None,
                    tone_score=jd_rec.get("tone_score") or 0.0,
                ),
                version=jd_rec.get("version", 1),
                error_message=brief.get("error_message"),
            )

    return StatusResponse(
        thread_id=thread_id,
        status=brief_status,
        error_message=brief.get("error_message"),
    )


@router.post("/review/{thread_id}", response_model=ReviewDecisionResponse)
def submit_review_decision(
    thread_id: str,
    decision: ReviewDecisionInput,
    background_tasks: BackgroundTasks,
):
    """Accept a review decision (approve / edit / revise) and resume the graph."""
    brief = db_ops.get_role_brief_by_thread(thread_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Thread not found")
    brief_status = brief.get("status", RoleBriefStatus.PENDING)
    if isinstance(brief_status, str):
        pass
    else:
        brief_status = brief_status.value if hasattr(brief_status, "value") else str(brief_status)
    if brief_status != RoleBriefStatus.PENDING_REVIEW:
        raise HTTPException(status_code=400, detail="Job is not pending review")

    # Enforce max-revision guard before resuming
    config = {"configurable": {"thread_id": thread_id}}
    try:
        with get_checkpointer() as cp:
            checkpoint = cp.get(config)
    except Exception:
        checkpoint = None

    if checkpoint is None:
        raise HTTPException(status_code=404, detail="No checkpoint found for this thread")

    channel_values = _get_channel_values(checkpoint)
    revision_count = (channel_values or {}).get("revision_count", 0)
    if decision.action == "revise" and revision_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum 3 revisions reached. Please use inline edit instead.",
        )

    decision_state: dict = {"review_decision": decision.action.value}
    if decision.action == "edit" and decision.edited_jd:
        decision_state["edited_jd"] = decision.edited_jd.dict()
    elif decision.action == "revise" and decision.feedback:
        decision_state["feedback"] = decision.feedback

    background_tasks.add_task(resume_graph_background, thread_id, decision_state)

    new_status = "publishing" if decision.action.value in ("approve", "edit") else "generating"
    return ReviewDecisionResponse(success=True, message="Review decision submitted", new_status=new_status)


@router.get("/published/{thread_id}", response_model=PublishedJDResponse)
def get_published_jd(thread_id: str):
    """Fetch the final published job description."""
    jd = db_ops.get_job_description_by_thread_status(thread_id, JDStatus.PUBLISHED)
    if not jd:
        raise HTTPException(status_code=404, detail="Published JD not found")

    published_at = jd.get("published_at")
    if hasattr(published_at, "isoformat"):
        published_at = published_at.isoformat()
    elif published_at:
        published_at = str(published_at)

    return PublishedJDResponse(
        thread_id=thread_id,
        jd_content=JDContent(**jd["jd_content"]),
        published_at=published_at or "",
        version=jd.get("version", 1),
    )
