from pymongo import MongoClient
from core.config import get_settings

_settings = get_settings()
_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    """Return a single shared MongoClient with TLS config for Atlas."""
    global _client
    if _client is None:
        _client = MongoClient(
            _settings.MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
        )
    return _client


def get_db():
    return get_mongo_client()["talynx"]


def get_role_briefs():
    return get_db()["role_briefs"]


def get_job_descriptions():
    return get_db()["job_descriptions"]


def get_sourcing_queue():
    return get_db()["sourcing_queue"]


def get_shortlisted_candidates():
    return get_db()["shortlisted_candidates"]