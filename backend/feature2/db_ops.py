"""MongoDB operations for Feature 2."""
from datetime import datetime
from core.mongodb import get_job_descriptions, get_sourcing_queue, get_shortlisted_candidates, get_sourcing_candidates
from feature1.models import JDStatus, SourcingQueueStatus
from bson.objectid import ObjectId


def get_published_jd(thread_id: str) -> dict | None:
    return get_job_descriptions().find_one(
        {"thread_id": thread_id, "status": JDStatus.PUBLISHED},
        sort=[("version", -1)],
    )


def get_sourcing_queue_entry(thread_id: str) -> dict | None:
    return get_sourcing_queue().find_one({"thread_id": thread_id})


def update_sourcing_queue_status(thread_id: str, status: str):
    get_sourcing_queue().update_one(
        {"thread_id": thread_id},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}},
    )


def insert_sourcing_candidates(candidates: list[dict]):
    """Insert multiple candidates into the sourcing_candidates collection."""
    if not candidates:
        return
    for c in candidates:
        if "created_at" not in c:
            c["created_at"] = datetime.utcnow()
        if "updated_at" not in c:
            c["updated_at"] = datetime.utcnow()
    get_sourcing_candidates().insert_many(candidates)


def get_sourcing_candidates_by_job(job_id: str) -> list[dict]:
    """Retrieve all tracked candidates for a job/thread."""
    cursor = get_sourcing_candidates().find({"job_id": job_id}).sort("score", -1)
    return list(cursor)


def update_candidate_status(candidate_id: str, new_status: str) -> dict | None:
    """Update a candidate's status natively using ObjectId."""
    from pymongo import ReturnDocument
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None
        
    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {"$set": {
            "status": new_status,
            "updated_at": datetime.utcnow(),
        }},
        return_document=ReturnDocument.AFTER
    )
