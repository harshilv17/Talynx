"""MongoDB operations for Feature 2."""
from datetime import datetime
from core.mongodb import get_job_descriptions, get_sourcing_queue, get_shortlisted_candidates
from feature1.models import JDStatus, SourcingQueueStatus


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


def insert_shortlisted_candidates(thread_id: str, candidates: list) -> dict:
    doc = {
        "thread_id": thread_id,
        "candidates": candidates,
        "created_at": datetime.utcnow(),
    }
    result = get_shortlisted_candidates().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def get_shortlisted_by_thread(thread_id: str) -> dict | None:
    return get_shortlisted_candidates().find_one(
        {"thread_id": thread_id},
        sort=[("created_at", -1)],
    )
