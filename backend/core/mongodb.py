from pymongo import MongoClient
from core.config import get_settings

_settings = get_settings()
_client: MongoClient | None = None


import logging
logger = logging.getLogger(__name__)

def get_mongo_client() -> MongoClient:
    """Return a single shared MongoClient."""
    global _client
    if _client is None:
        logger.info("[MongoDB] Initializing MongoDB client...")
        uri = _settings.MONGO_URI
        use_tls = uri.startswith("mongodb+srv://")
        kwargs: dict = {
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 5000,
            "socketTimeoutMS": 10000,
        }
        if use_tls:
            kwargs["tls"] = True
            kwargs["tlsAllowInvalidCertificates"] = True
        
        try:
            _client = MongoClient(uri, **kwargs)
            logger.info("[MongoDB] Client initialized successfully.")
        except Exception as e:
            logger.error(f"[MongoDB] Client initialization failed: {e}")
            raise
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