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
    GITHUB_TOKEN: str | None = None

    # ── Outreach / email provider (Feature 3) ─────────────────────────────
    # Resend (primary): set RESEND_API_KEY to enable
    RESEND_API_KEY: str | None = None
    # SMTP (fallback): set SMTP_HOST to enable
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    # Sender address used by both providers
    OUTREACH_FROM_EMAIL: str = "noreply@talynx.ai"

    model_config = {
        "env_file": _find_env_file(),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

@lru_cache()
def get_settings() -> Settings:
    print("Loading ENV from:", _find_env_file())
    return Settings()
