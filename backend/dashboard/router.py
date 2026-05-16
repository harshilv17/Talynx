from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from core.mongodb import get_role_briefs, get_sourcing_candidates

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/")
def get_dashboard():
    # 1. Fetch all jobs (exclude soft-deleted)
    role_briefs = list(get_role_briefs().find({"is_deleted": {"$ne": True}}).sort("created_at", -1))
    
    jobs = []
    for rb in role_briefs:
        thread_id = rb.get("thread_id")
        title = rb.get("job_title", rb.get("role_title", "Untitled Role"))
        
        # Determine pipeline status
        pipeline_status = rb.get("pipeline_status", "ACTIVE")
        
        # Calculate duration
        created_at = rb.get("created_at")
        completed_at = rb.get("completed_at")
        end_time = completed_at if completed_at else datetime.now(timezone.utc).isoformat()
        
        try:
            # Simple days difference approximation
            if isinstance(created_at, str):
                created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            else:
                created_dt = created_at
            
            if isinstance(end_time, str):
                end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            else:
                end_dt = end_time
                
            duration_days = (end_dt - created_dt).days
        except Exception:
            duration_days = 0
            
        # 2. Count candidates by status
        candidates = list(get_sourcing_candidates().find({"job_id": thread_id}))
        total = len(candidates)
        
        status_counts = {}
        for c in candidates:
            s = c.get("status", "pending")
            status_counts[s] = status_counts.get(s, 0) + 1
            
        shortlisted = status_counts.get("shortlisted", 0)
        rejected = status_counts.get("rejected", 0)
        saved = status_counts.get("saved", 0)
        pending = status_counts.get("pending", 0)
        hired = status_counts.get("hired", 0)
        
        hired_candidates = [c.get("name") for c in candidates if c.get("status") == "hired"]
        
        jobs.append({
            "job_id": thread_id,
            "title": title,
            "pipeline_status": pipeline_status,
            "duration_days": max(0, duration_days),
            "created_at": created_at,
            "stats": {
                "total": total,
                "shortlisted": shortlisted,
                "rejected": rejected,
                "saved": saved,
                "pending": pending,
                "hired": hired
            },
            "hired_candidates": hired_candidates
        })
        
    return {"jobs": jobs}

# ── Lifecycle Actions ─────────────────────────────────────────────────────────

@router.patch("/pipeline/{job_id}/complete")
def complete_pipeline(job_id: str):
    """Mark a pipeline as COMPLETED (hiring closed)."""
    res = get_role_briefs().update_one(
        {"thread_id": job_id},
        {"$set": {
            "pipeline_status": "COMPLETED",
            "completed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"success": True, "message": "Pipeline marked as completed"}

@router.patch("/pipeline/{job_id}/archive")
def archive_pipeline(job_id: str):
    """Archive a pipeline (hide from active dashboard)."""
    res = get_role_briefs().update_one(
        {"thread_id": job_id},
        {"$set": {
            "pipeline_status": "ARCHIVED",
            "archived_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"success": True, "message": "Pipeline archived"}

@router.patch("/pipeline/{job_id}/restore")
def restore_pipeline(job_id: str):
    """Restore an archived or completed pipeline to ACTIVE."""
    res = get_role_briefs().update_one(
        {"thread_id": job_id},
        {"$set": {"pipeline_status": "ACTIVE"}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"success": True, "message": "Pipeline restored to active"}

@router.delete("/pipeline/{job_id}")
def delete_pipeline(job_id: str):
    """Soft delete a pipeline."""
    res = get_role_briefs().update_one(
        {"thread_id": job_id},
        {"$set": {
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return {"success": True, "message": "Pipeline soft deleted"}

