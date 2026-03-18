from contextlib import contextmanager
from langgraph.checkpoint.mongodb import MongoDBSaver
from core.config import get_settings

settings = get_settings()


@contextmanager
def get_checkpointer():
    """Yield a MongoDBSaver checkpointer backed by MongoDB.

    Usage:
        with get_checkpointer() as cp:
            graph = create_feature1_graph(cp)
            graph.invoke(state, config)
    """
    with MongoDBSaver.from_conn_string(
        settings.MONGODB_URI,
        db_name=f"{settings.MONGODB_DB_NAME}_checkpoints",
    ) as checkpointer:
        yield checkpointer
