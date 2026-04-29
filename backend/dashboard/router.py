from fastapi import APIRouter
from core.mongodb import get_role_briefs, get_sourcing_candidates

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

@router.get("/")
def get_dashboard():
    # 1. Fetch all jobs
    role_briefs = list(get_role_briefs().find().sort("created_at", -1))
    
    jobs = []
    for rb in role_briefs:
        thread_id = rb.get("thread_id")
        title = rb.get("job_title", rb.get("role_title", "Untitled Role"))
        status = rb.get("status", "pending")
        
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
        
        # 3 & 4. Fetch outreach and offer data (Mocked based on pipeline status since Feature 3/4 mock transitions)
        contacted = status_counts.get("contacted", 0) + status_counts.get("interviewed", 0) + status_counts.get("evaluated", 0) + status_counts.get("offered", 0) + status_counts.get("hired", 0)
        offered = status_counts.get("offered", 0) + status_counts.get("hired", 0)
        hired = status_counts.get("hired", 0)
        
        hired_candidates = [c.get("name") for c in candidates if c.get("status") == "hired"]
        
        jobs.append({
            "job_id": thread_id,
            "title": title,
            "status": status,
            "stats": {
                "total": total,
                "shortlisted": shortlisted,
                "rejected": rejected,
                "saved": saved,
                "pending": pending
            },
            "outreach": {
                "emails_sent": contacted,
                "responses": contacted // 2 if contacted > 0 else 0
            },
            "offers": {
                "generated": offered,
                "accepted": hired,
                "hired_candidates": hired_candidates
            }
        })
        
    return {"jobs": jobs}
