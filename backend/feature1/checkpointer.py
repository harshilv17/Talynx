from contextlib import contextmanager
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from core.config import get_settings

settings = get_settings()


@contextmanager
def get_checkpointer():
    """Yield a MongoDBSaver checkpointer backed by MongoDB Atlas.

    We create our own MongoClient with TLS config because
    MongoDBSaver.from_conn_string() does not pass TLS options
    to its internal MongoClient.

    Usage:
        with get_checkpointer() as cp:
            graph = create_feature1_graph(cp)
            graph.invoke(state, config)
    """
    client = None
    try:
        client = MongoClient(
            settings.MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
        )
        yield MongoDBSaver(
            client,
            db_name="talynx_checkpoints",
        )
    finally:
        if client:
            client.close()