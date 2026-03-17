from langgraph.checkpoint.postgres import PostgresSaver
from psycopg2.pool import SimpleConnectionPool
from core.config import get_settings

settings = get_settings()


def get_checkpointer() -> PostgresSaver:
    """Create and return a PostgresSaver checkpointer for LangGraph."""
    
    db_url = settings.DATABASE_URL.replace('postgresql://', 'postgres://')
    
    pool = SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        dsn=db_url
    )
    
    return PostgresSaver(pool)
