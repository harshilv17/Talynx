from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from bson.objectid import ObjectId

from core.mongodb import assert_pipeline_active
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

import logging
import traceback

def run_sourcing_background(thread_id: str, initial_state: Feature2State):
    logging.info(f"[Feature2] run_sourcing_background STARTED for {thread_id}")
    try:
        logging.info(f"[Feature2] Creating graph for {thread_id}")
        graph = create_feature2_graph()
        logging.info(f"[Feature2] Graph created. Invoking initial state for {thread_id}...")
        graph.invoke(initial_state)
        logging.info(f"[Feature2] Graph invocation COMPLETED for {thread_id}")
    except Exception as e:
        logging.error(f"[Feature2] PIPELINE CRASHED in background task: {traceback.format_exc()}")
        db_ops.update_sourcing_progress(thread_id, "failed", error_message=f"Pipeline crashed: {str(e)}")


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@router.post("/start-sourcing/{thread_id}", response_model=StartSourcingResponse)
def start_sourcing(thread_id: str, background_tasks: BackgroundTasks):
    """Trigger the Feature 2 sourcing workflow for a published JD."""
    assert_pipeline_active(thread_id)

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
        "status": "in_progress",
        "error_message": None,
    }

    from datetime import datetime
    get_sourcing_queue = db_ops.get_sourcing_queue
    
    import logging
    logging.info(f"[Feature2] /start-sourcing called for {thread_id}. Attempting to update initial DB state...")
    
    try:
        res = get_sourcing_queue().update_one(
            {"thread_id": thread_id},
            {"$set": {
                "status": "in_progress",
                "stage": "initializing",
                "progress": 0,
                "message": "Initializing sourcing pipeline...",
                "started_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        logging.info(f"[Feature2] Initial DB update result for {thread_id}: matched={res.matched_count}, modified={res.modified_count}")
    except Exception as db_e:
        logging.error(f"[Feature2] DB update failed during start_sourcing: {db_e}")
        raise HTTPException(status_code=500, detail="Failed to initialize pipeline state in DB.")

    logging.info(f"[Feature2] Queuing background task for {thread_id}")
    background_tasks.add_task(run_sourcing_background, thread_id, initial_state)
    logging.info(f"[Feature2] /start-sourcing endpoint complete for {thread_id}")
    return StartSourcingResponse(thread_id=thread_id, status="in_progress")


@router.get("/status/{thread_id}", response_model=SourcingStatusResponse)
def get_sourcing_status(thread_id: str):
    """Return current sourcing status and shortlisted candidates if complete."""
    import logging
    import traceback
    try:
        sourcing_entry = db_ops.get_sourcing_queue_entry(thread_id)
        if not sourcing_entry:
            raise HTTPException(status_code=404, detail="No sourcing queue entry found for this thread")

        current_status = sourcing_entry.get("status", SourcingQueueStatus.PENDING)

        from datetime import datetime
        started_at = sourcing_entry.get("started_at")
        
        elapsed = 0
        if started_at:
            if isinstance(started_at, str):
                try:
                    started_at = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                except Exception:
                    pass

            end_time = sourcing_entry.get("updated_at") if current_status in ["completed", "failed"] else datetime.utcnow()
            
            if isinstance(end_time, str):
                try:
                    end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                except Exception:
                    end_time = datetime.utcnow()
                    
            if end_time and started_at and isinstance(end_time, datetime) and isinstance(started_at, datetime):
                # Ensure timezone offset comparability
                if started_at.tzinfo and not end_time.tzinfo:
                    started_at = started_at.replace(tzinfo=None)
                elif end_time.tzinfo and not started_at.tzinfo:
                    end_time = end_time.replace(tzinfo=None)
                
                try:
                    elapsed = int((end_time - started_at).total_seconds())
                except Exception as dt_e:
                    logging.error(f"Datetime subtraction error: {dt_e}")
                    elapsed = 0

            # ORPHANED JOB DETECTION:
            # If the job is marked as in_progress but hasn't updated its progress in the DB 
            # for more than 180 seconds, the background thread has silently crashed or died.
            if current_status == "in_progress":
                last_updated = sourcing_entry.get("updated_at")
                if isinstance(last_updated, str):
                    try:
                        last_updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                    except Exception:
                        last_updated = datetime.utcnow()
                
                if last_updated and isinstance(last_updated, datetime):
                    if last_updated.tzinfo:
                        last_updated = last_updated.replace(tzinfo=None)
                    
                    idle_time = (datetime.utcnow() - last_updated).total_seconds()
                    if idle_time > 180:
                        logging.error(f"[Feature2] Orphaned job detected for {thread_id}. Idle for {idle_time}s. Failing.")
                        db_ops.update_sourcing_progress(
                            thread_id, 
                            "failed", 
                            error_message="Pipeline execution crashed silently or timed out. Please retry."
                        )
                        current_status = "failed"
                        sourcing_entry["error_message"] = "Pipeline execution crashed silently or timed out. Please retry."

        status_map = {
            SourcingQueueStatus.PENDING: "pending",
            SourcingQueueStatus.IN_PROGRESS: "in_progress",
        }

        return SourcingStatusResponse(
            thread_id=thread_id,
            status=status_map.get(current_status, current_status),
            stage=sourcing_entry.get("stage"),
            progress=sourcing_entry.get("progress", 0),
            message=sourcing_entry.get("message"),
            error_message=sourcing_entry.get("error_message"),
            elapsed_seconds=elapsed,
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in get_sourcing_status: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Status polling error: {str(e)}")


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
            response=c.get("response"),
            evaluation=c.get("evaluation"),
            notes=c.get("notes"),
            rejection_feedback=c.get("rejection_feedback"),
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
                response=c.get("response"),
                evaluation=c.get("evaluation"),
                notes=c.get("notes"),
                rejection_feedback=c.get("rejection_feedback"),
            ))
            
    return SourcingCandidatesResponse(job_id=jd_id, candidates=candidates)

@router.post("/candidate/{candidate_id}/{action}", response_model=CandidateActionResponse)
def update_candidate_action(candidate_id: str, action: str, payload: CandidateActionRequest = None):
    """Update a candidate's status (shortlist, reject, save)."""
    # Fetch candidate to get job_id
    candidate = db_ops.get_sourcing_candidates().find_one({"_id": ObjectId(candidate_id)})
    if candidate:
        assert_pipeline_active(candidate.get("job_id"))

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

class NotesUpdateRequest(BaseModel):
    notes: str

@router.patch("/candidate/{candidate_id}/notes")
def update_candidate_notes(candidate_id: str, payload: NotesUpdateRequest):
    """Update HR notes for a candidate."""
    from bson.objectid import ObjectId
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    
    updated = db_ops.get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {"$set": {"notes": payload.notes}},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    return {"success": True, "notes": payload.notes}

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

