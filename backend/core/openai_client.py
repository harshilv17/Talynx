from openai import OpenAI
from core.config import get_settings
from functools import lru_cache

settings = get_settings()


@lru_cache()
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.OPENAI_API_KEY)
