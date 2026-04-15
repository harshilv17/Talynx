from groq import Groq
from core.config import get_settings
from functools import lru_cache

settings = get_settings()


@lru_cache()
def get_groq_client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)
