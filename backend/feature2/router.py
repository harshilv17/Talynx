from fastapi import APIRouter, HTTPException, BackgroundTasks

from feature2.schemas import (
    StartSourcingResponse, SourcingStatusResponse, 
    CandidateResult, SourcingCandidatesResponse, CandidateActionResponse,
    CandidateActionRequest
)
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
        "role_brief": None,
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
        return SourcingStatusResponse(
            thread_id=thread_id,
            status="completed",
        )

    status_map = {
        SourcingQueueStatus.PENDING: "pending",
        SourcingQueueStatus.IN_PROGRESS: "in_progress",
    }

    return SourcingStatusResponse(
        thread_id=thread_id,
        status=status_map.get(current_status, current_status),
    )


@router.get("/candidates", response_model=SourcingCandidatesResponse)
def get_sourcing_candidates(job_id: str):
    """Fetch all sourced candidates for a given job."""
    db_candidates = db_ops.get_sourcing_candidates_by_job(job_id)
    
    candidates = []
    for c in db_candidates:
        candidates.append(CandidateResult(
            id=str(c["_id"]),
            name=c["name"],
            skills=c.get("skills", []),
            experience=c.get("experience", 0),
            score=c.get("score", 0),
            status=c.get("status", "pending"),
            rejection_reason=c.get("rejection_reason"),
            resume_text=c.get("resume_text", ""),
            source=c.get("source", "github"),
        ))
        
    return SourcingCandidatesResponse(job_id=job_id, candidates=candidates)


@router.get("/shortlisted", response_model=SourcingCandidatesResponse)
def get_shortlisted_candidates(jd_id: str):
    """Fetch only shortlisted candidates for a given job."""
    db_candidates = db_ops.get_sourcing_candidates_by_job(jd_id)
    
    candidates = []
    for c in db_candidates:
        if c.get("status") == "shortlisted":
            candidates.append(CandidateResult(
                id=str(c["_id"]),
                name=c["name"],
                skills=c.get("skills", []),
                experience=c.get("experience", 0),
                score=c.get("score", 0),
                status=c.get("status", "pending"),
                rejection_reason=c.get("rejection_reason"),
                resume_text=c.get("resume_text", ""),
                source=c.get("source", "github"),
            ))
            
    return SourcingCandidatesResponse(job_id=jd_id, candidates=candidates)

@router.post("/candidate/{candidate_id}/{action}", response_model=CandidateActionResponse)
def update_candidate_action(candidate_id: str, action: str, payload: CandidateActionRequest = None):
    """Update a candidate's status (shortlist, reject, save)."""
    print(f"[DEBUG] Received CandidateActionRequest: {payload}")
    valid_actions = {"shortlist", "reject", "save"}
    if action not in valid_actions:
        raise HTTPException(status_code=400, detail=f"Invalid action. Must be one of {valid_actions}")
        
    new_status = payload.status if payload else action
    if not payload:
        if action == "shortlist":
            new_status = "shortlisted"
        elif action == "save":
            new_status = "saved"
        elif action == "reject":
            new_status = "rejected"
        
    try:
        updated = db_ops.update_candidate_status(candidate_id, new_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not updated:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return CandidateActionResponse(
        success=True,
        new_status=new_status,
        message=f"Candidate marked as {new_status}",
    )

from pydantic import BaseModel

class CompleteSourcingRequest(BaseModel):
    job_id: str

@router.post("/complete")
def complete_sourcing(request: CompleteSourcingRequest):
    """Transition to Feature 3 by completing Feature 2."""
    candidates = db_ops.get_sourcing_candidates_by_job(request.job_id)
    shortlisted = [c for c in candidates if c.get("status") == "shortlisted"]
    
    return {
        "next": f"/feature3/outreach?jdId={request.job_id}",
        "count": len(shortlisted)
    }

