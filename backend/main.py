from pathlib import Path
from dotenv import load_dotenv

# Load .env before any config is read
_env_path = Path(__file__).resolve().parent / ".env"
if not _env_path.exists():
    _env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from feature1.router import router as feature1_router
from feature2.router import router as feature2_router

app = FastAPI(


    title="ATA - Autonomous Talent Acquisition",
    description="AI-powered hiring automation system",
    version="1.0.0"
)

import os
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://frontend:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class NormalizePathMiddleware(BaseHTTPMiddleware):
    """Normalize double slashes in path to fix frontend URL issues."""
    async def dispatch(self, request: Request, call_next):
        if "//" in request.url.path:
            path = request.url.path.replace("//", "/")
            scope = dict(request.scope)
            scope["path"] = path
            request = Request(scope)
        return await call_next(request)


app.add_middleware(NormalizePathMiddleware)
app.include_router(feature1_router)
app.include_router(feature2_router)


@app.get("/")
def root():
    return {
        "message": "ATA API is running",
        "version": "1.0.0",
        "features": ["feature1", "feature2"]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
def test_db_connection():
    from core.mongodb import get_mongo_client
    try:
        get_mongo_client().admin.command("ping")
        print("✅ MongoDB Atlas connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
