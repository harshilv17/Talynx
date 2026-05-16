"""MongoDB CRUD operations for rejection feedback."""
from datetime import datetime, timezone
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from core.mongodb import get_sourcing_candidates
import logging

logger = logging.getLogger(__name__)


def save_feedback(candidate_id: str, feedback: dict) -> dict | None:
    """Store generated feedback in the candidate document."""
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {"$set": {
            "rejection_feedback": feedback,
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=ReturnDocument.AFTER,
    )


def get_feedback(candidate_id: str) -> dict | None:
    """Retrieve feedback for a candidate."""
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    doc = get_sourcing_candidates().find_one(
        {"_id": oid},
        {"rejection_feedback": 1, "name": 1, "status": 1},
    )
    return doc


def mark_feedback_sent(candidate_id: str) -> dict | None:
    """Mark feedback email as sent."""
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {"$set": {
            "rejection_feedback.email_sent": True,
            "rejection_feedback.email_sent_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }},
        return_document=ReturnDocument.AFTER,
    )


def get_all_feedback_for_job(job_id: str) -> list[dict]:
    """Retrieve all candidates with feedback for a given job."""
    return list(get_sourcing_candidates().find(
        {
            "job_id": job_id,
            "rejection_feedback": {"$exists": True},
        },
        {
            "name": 1, "status": 1,
            "rejection_feedback.version": 1,
            "rejection_feedback.generated_at": 1,
            "rejection_feedback.email_sent": 1,
        },
    ))
