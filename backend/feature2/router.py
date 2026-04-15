from fastapi import APIRouter, HTTPException, BackgroundTasks

from feature2.schemas import StartSourcingResponse, SourcingStatusResponse, CandidateResult
from feature2.state import Feature2State
from feature2.graph import create_feature2_graph
from feature2 import db_ops
from feature1.models import SourcingQueueStatus

router = APIRouter(prefix="/api/v1/feature2", tags=["feature2"])


# ─────────────────────────────────────────────
# Background task helper
# ─────────────────────────────────────────────

def run_sourcing_background(thread_id: str, initial_state: Feature2State):
    try:
        graph = create_feature2_graph()
        graph.invoke(initial_state)
    except Exception as e:
        db_ops.update_sourcing_queue_status(thread_id, SourcingQueueStatus.PENDING)


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.post("/start-sourcing/{thread_id}", response_model=StartSourcingResponse)
def start_sourcing(thread_id: str, background_tasks: BackgroundTasks):
    """Trigger the Feature 2 sourcing workflow for a published JD."""

    sourcing_entry = db_ops.get_sourcing_queue_entry(thread_id)
    if not sourcing_entry:
        raise HTTPException(status_code=404, detail="No sourcing queue entry found for this thread")

    current_status = sourcing_entry.get("status", "")
    if current_status == SourcingQueueStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Sourcing already completed for this thread")

    if current_status == SourcingQueueStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Sourcing already in progress for this thread")

    jd_doc = db_ops.get_published_jd(thread_id)
    if not jd_doc:
        raise HTTPException(status_code=404, detail="No published JD found for this thread")

    initial_state: Feature2State = {
        "thread_id": thread_id,
        "jd_content": None,
        "candidates": None,
        "jd_embedding": None,
        "candidate_embeddings": None,
        "ranked_candidates": None,
        "shortlisted": None,
        "status": "pending",
        "error_message": None,
    }

    background_tasks.add_task(run_sourcing_background, thread_id, initial_state)
    return StartSourcingResponse(thread_id=thread_id, status="in_progress")


@router.get("/status/{thread_id}", response_model=SourcingStatusResponse)
def get_sourcing_status(thread_id: str):
    """Return current sourcing status and shortlisted candidates if complete."""

    sourcing_entry = db_ops.get_sourcing_queue_entry(thread_id)
    if not sourcing_entry:
        raise HTTPException(status_code=404, detail="No sourcing queue entry found for this thread")

    current_status = sourcing_entry.get("status", SourcingQueueStatus.PENDING)

    if current_status == SourcingQueueStatus.COMPLETED:
        shortlisted_doc = db_ops.get_shortlisted_by_thread(thread_id)
        candidates = []
        if shortlisted_doc and shortlisted_doc.get("candidates"):
            candidates = [
                CandidateResult(
                    name=c["name"],
                    skills=c["skills"],
                    experience=c["experience"],
                    match_score=c["match_score"],
                    resume_text=c["resume_text"],
                )
                for c in shortlisted_doc["candidates"]
            ]

        return SourcingStatusResponse(
            thread_id=thread_id,
            status="completed",
            shortlisted_candidates=candidates,
        )

    status_map = {
        SourcingQueueStatus.PENDING: "pending",
        SourcingQueueStatus.IN_PROGRESS: "in_progress",
    }

    return SourcingStatusResponse(
        thread_id=thread_id,
        status=status_map.get(current_status, current_status),
    )
