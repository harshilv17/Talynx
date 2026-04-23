"""MongoDB operations for Feature 3 — Outreach."""
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument

from core.mongodb import get_sourcing_candidates
from feature4.states import CandidateStatus


def save_outreach_success(
    candidate_id: str,
    email_address: str,
    subject: str,
    body: str,
) -> dict | None:
    """
    Persist a successful outreach record and advance the candidate to CONTACTED.
    Returns the updated document, or None if the candidate is not found.
    """
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    now = datetime.utcnow()
    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {
            "$set": {
                "outreach": {
                    "email_address": email_address,
                    "email_subject": subject,
                    "email_body":    body,
                    "sent_at":       now,
                    "status":        "sent",
                    "error":         None,
                },
                "status":       CandidateStatus.CONTACTED,
                "contacted_at": now,
                "updated_at":   now,
            }
        },
        return_document=ReturnDocument.AFTER,
    )


def save_outreach_failure(
    candidate_id: str,
    email_address: str,
    subject: str,
    body: str,
    error: str,
) -> dict | None:
    """
    Persist a failed outreach attempt WITHOUT changing the candidate status.
    Stores the generated email content so it can be retried later.
    Returns the updated document, or None if the candidate is not found.
    """
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {
            "$set": {
                "outreach": {
                    "email_address": email_address,
                    "email_subject": subject,
                    "email_body":    body,
                    "sent_at":       None,
                    "status":        "failed",
                    "error":         error,
                },
                "updated_at": datetime.utcnow(),
            }
        },
        return_document=ReturnDocument.AFTER,
    )


def get_candidates_with_failed_outreach(job_id: str) -> list[dict]:
    """Return candidates for a job whose last outreach attempt failed."""
    return list(
        get_sourcing_candidates().find(
            {"job_id": job_id, "outreach.status": "failed"}
        )
    )
