"""MongoDB operations for Feature 4 — Evaluation & Offer."""
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument

from core.mongodb import get_sourcing_candidates
from feature4.states import CandidateStatus, assert_valid_transition


def get_candidate_by_id(candidate_id: str) -> dict | None:
    """Fetch a single candidate document by its MongoDB _id."""
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None
    return get_sourcing_candidates().find_one({"_id": oid})


def get_candidates_by_ids(candidate_ids: list[str]) -> list[dict]:
    """Fetch multiple candidate documents by their MongoDB _ids."""
    oids = []
    for cid in candidate_ids:
        try:
            oids.append(ObjectId(cid))
        except Exception:
            pass
    if not oids:
        return []
    return list(get_sourcing_candidates().find({"_id": {"$in": oids}}))


def get_candidates_for_processing(job_id: str) -> list[dict]:
    """Fetch candidates eligible for the automation pipeline.

    Includes INTERVIEWED (need evaluation + decision) and EVALUATED
    (need offer or rejection action taken).
    """
    return list(get_sourcing_candidates().find({
        "job_id": job_id,
        "status": {"$in": [
            CandidateStatus.INTERVIEWED.value,
            CandidateStatus.EVALUATED.value,
        ]},
    }))


def mark_candidate_offered(candidate_id: str, offer_text: str) -> dict | None:
    """Advance candidate status to OFFERED and store the offer letter."""
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    doc = get_sourcing_candidates().find_one({"_id": oid}, {"status": 1})
    if not doc:
        return None
    assert_valid_transition(doc.get("status", ""), CandidateStatus.OFFERED.value)

    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {"$set": {
            "status":     CandidateStatus.OFFERED,
            "offer":      {"text": offer_text, "sent_at": datetime.utcnow()},
            "updated_at": datetime.utcnow(),
        }},
        return_document=ReturnDocument.AFTER,
    )

def mark_candidate_hired(candidate_id: str) -> dict | None:
    """Advance candidate status to HIRED and close the JD."""
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    doc = get_sourcing_candidates().find_one({"_id": oid}, {"status": 1, "job_id": 1})
    if not doc:
        return None
    assert_valid_transition(doc.get("status", ""), CandidateStatus.HIRED.value)

    updated = get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {"$set": {
            "status":      CandidateStatus.HIRED,
            "hired_at":    datetime.utcnow(),
            "updated_at":  datetime.utcnow(),
        }},
        return_document=ReturnDocument.AFTER,
    )
    
    # Close the JD
    from core.mongodb import get_jd_collection
    get_jd_collection().update_one(
        {"job_id": doc.get("job_id")},
        {"$set": {"status": "closed"}}
    )
    return updated


def mark_candidate_rejected(candidate_id: str) -> dict | None:
    """Advance candidate status to REJECTED."""
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    doc = get_sourcing_candidates().find_one({"_id": oid}, {"status": 1})
    if not doc:
        return None
    assert_valid_transition(doc.get("status", ""), CandidateStatus.REJECTED.value)

    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {"$set": {
            "status":      CandidateStatus.REJECTED,
            "rejected_at": datetime.utcnow(),
            "updated_at":  datetime.utcnow(),
        }},
        return_document=ReturnDocument.AFTER,
    )


def save_evaluation(candidate_id: str, evaluation: dict, decision: dict) -> dict | None:
    """
    Persist evaluation scorecard + hire decision into the candidate document
    and advance its status to EVALUATED.

    Returns the updated document, or None if the candidate was not found.
    """
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        return None

    return get_sourcing_candidates().find_one_and_update(
        {"_id": oid},
        {
            "$set": {
                "evaluation":   evaluation,
                "decision":     decision,
                "status":       CandidateStatus.EVALUATED,
                "evaluated_at": datetime.utcnow(),
                "updated_at":   datetime.utcnow(),
            }
        },
        return_document=ReturnDocument.AFTER,
    )
