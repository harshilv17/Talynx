from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path

def _find_env_file() -> str:
    candidates = [
        Path(__file__).parent.parent.parent / ".env",
        Path(__file__).parent.parent / ".env",
        Path(".env"),
    ]
    for p in candidates:
        if p.exists():
            return str(p)
    return ".env"


class Settings(BaseSettings):
    GROQ_API_KEY: str
    MONGO_URI: str

    model_config = {
        "env_file": _find_env_file(),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

@lru_cache()
def get_settings() -> Settings:
    print("Loading ENV from:", _find_env_file())
    return Settings()
