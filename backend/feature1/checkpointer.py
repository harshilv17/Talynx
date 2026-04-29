from contextlib import contextmanager
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os

# Store checkpoint DB in a writable location (Render uses /tmp for ephemeral data)
_DB_PATH = os.environ.get("CHECKPOINT_DB_PATH", "checkpoints.db")


@contextmanager
def get_checkpointer():
    """Yield a SqliteSaver checkpointer backed by a local SQLite file.

    Lightweight alternative to MongoDBSaver — avoids pulling in the
    heavy langchain-mongodb → langchain → torch dependency chain that
    causes OOM on Render's free 512 MB tier.

    Usage:
        with get_checkpointer() as cp:
            graph = create_feature1_graph(cp)
            graph.invoke(state, config)
    """
    conn = None
    try:
        conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
        yield SqliteSaver(conn)
    finally:
        if conn:
            conn.close()