"""MongoDB operations for Feature 1."""
from datetime import datetime
from core.mongodb import get_role_briefs, get_job_descriptions, get_sourcing_queue
from feature1.models import RoleBriefStatus, JDStatus, SourcingQueueStatus


def create_role_brief(thread_id: str, data: dict) -> dict:
    doc = {
        "thread_id": thread_id,
        "status": RoleBriefStatus.PENDING,
        **data,
        "created_at": datetime.utcnow(),
    }
    result = get_role_briefs().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def get_role_brief_by_thread(thread_id: str) -> dict | None:
    return get_role_briefs().find_one({"thread_id": thread_id})


def update_role_brief_status(thread_id: str, status: str, error_message: str | None = None):
    update = {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    if error_message is not None:
        update["$set"]["error_message"] = error_message
    get_role_briefs().update_one({"thread_id": thread_id}, update)


def insert_job_description(thread_id: str, role_brief_id, data: dict) -> dict:
    doc = {
        "role_brief_id": role_brief_id,
        "thread_id": thread_id,
        "version": data.get("version", 1),
        "status": data.get("status", JDStatus.PENDING_REVIEW),
        "jd_content": data["jd_content"],
        "guardrail_passed": data.get("guardrail_passed", 0),
        "guardrail_issues": data.get("guardrail_issues", []),
        "guardrail_corrected_jd": data.get("guardrail_corrected_jd"),
        "tone_score": data.get("tone_score"),
        "published_at": data.get("published_at"),
        "created_at": datetime.utcnow(),
    }
    result = get_job_descriptions().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


def get_job_description_by_thread_status(thread_id: str, status: str) -> dict | None:
    return get_job_descriptions().find_one(
        {"thread_id": thread_id, "status": status},
        sort=[("version", -1)]
    )


def get_job_description_by_thread_version(thread_id: str, version: int) -> dict | None:
    return get_job_descriptions().find_one(
        {"thread_id": thread_id, "version": version}
    )


def publish_job_description(thread_id: str, role_brief_id, version: int, jd_content: dict,
                             guardrail_passed: bool = True, guardrail_issues: list = None,
                             tone_score: float = 100.0) -> dict:
    """Publish JD: update existing or insert new. Returns the published JD doc with _id."""
    from pymongo import ReturnDocument
    existing = get_job_description_by_thread_version(thread_id, version)
    if existing:
        updated = get_job_descriptions().find_one_and_update(
            {"thread_id": thread_id, "version": version},
            {"$set": {
                "status": JDStatus.PUBLISHED,
                "jd_content": jd_content,
                "published_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }},
            return_document=ReturnDocument.AFTER
        )
        return updated or existing
    return insert_job_description(thread_id, role_brief_id, {
        "version": version,
        "status": JDStatus.PUBLISHED,
        "jd_content": jd_content,
        "guardrail_passed": 1 if guardrail_passed else 0,
        "guardrail_issues": guardrail_issues or [],
        "tone_score": tone_score,
        "published_at": datetime.utcnow(),
    })


def insert_sourcing_queue(role_brief_id, job_description_id, thread_id: str):
    get_sourcing_queue().insert_one({
        "role_brief_id": role_brief_id,
        "job_description_id": job_description_id,
        "thread_id": thread_id,
        "status": SourcingQueueStatus.PENDING,
        "created_at": datetime.utcnow(),
    })
