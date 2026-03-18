from pymongo import MongoClient
from core.config import get_settings

_settings = get_settings()
_client: MongoClient | None = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(_settings.MONGODB_URI)
    return _client


def get_db():
    return get_mongo_client()[_settings.MONGODB_DB_NAME]


def get_role_briefs():
    return get_db().role_briefs


def get_job_descriptions():
    return get_db().job_descriptions


def get_sourcing_queue():
    return get_db().sourcing_queue
