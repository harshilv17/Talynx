from pymongo import MongoClient
from core.config import get_settings

_settings = get_settings()
_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Return a single shared MongoClient.

    TLS is enabled only for Atlas (mongodb+srv:// URIs); local instances skip it.
    """
    global _client
    if _client is None:
        uri = _settings.MONGO_URI
        use_tls = uri.startswith("mongodb+srv://")
        kwargs: dict = {"serverSelectionTimeoutMS": 30000}
        if use_tls:
            kwargs["tls"] = True
            kwargs["tlsAllowInvalidCertificates"] = True
        _client = MongoClient(uri, **kwargs)
    return _client


def get_db():
    # Local instance uses "Talynx"; Atlas cluster uses "talynx".
    # Detect by URI scheme to stay consistent with whichever is in use.
    uri = _settings.MONGO_URI
    db_name = "talynx" if uri.startswith("mongodb+srv://") else "Talynx"
    return get_mongo_client()[db_name]


def get_role_briefs():
    return get_db()["role_briefs"]


def get_job_descriptions():
    return get_db()["job_descriptions"]


def get_sourcing_queue():
    return get_db()["sourcing_queue"]


def get_shortlisted_candidates():
    return get_db()["shortlisted_candidates"]

def get_sourcing_candidates():
    return get_db()["sourcing_candidates"]


def get_jd_collection():
    """Alias for get_job_descriptions — used by feature4.db_ops to close JDs."""
    return get_db()["job_descriptions"]


def assert_pipeline_active(job_id: str):
    """Raise HTTP 400 if the pipeline for this job_id is not ACTIVE."""
    from fastapi import HTTPException
    rb = get_role_briefs().find_one({"thread_id": job_id})
    if not rb:
        return
    status = rb.get("pipeline_status", "ACTIVE")
    if status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail=f"Action not allowed. Pipeline is currently {status}."
        )