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
from feature3.router import router as feature3_router
from feature4.router import router as feature4_router
from feature4.router import candidates_router
from feature4.feedback.router import router as feedback_router
from dashboard.router import router as dashboard_router

app = FastAPI(


    title="ATA - Autonomous Talent Acquisition",
    description="AI-powered hiring automation system",
    version="1.0.0"
)

import os
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse CORS origins from env, with fallbacks including Vercel deployment
env_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://frontend:3000,https://talynx.vercel.app")
_cors_origins = [o.strip() for o in env_origins.split(",") if o.strip()]

logger.info(f"CORS origins configured: {_cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} Method: {request.method} Status: {response.status_code} Time: {process_time:.4f}s")
    return response


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
app.include_router(feature3_router)
app.include_router(feature4_router)
app.include_router(candidates_router)
app.include_router(feedback_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "ATA API is running",
        "version": "1.0.0",
        "features": ["feature1", "feature2"]
    }


@app.get("/api/v1/system/status")
def system_status():
    return {
        "status": "healthy",
        "service": "talynx-api"
    }


@app.on_event("startup")
def startup_event():
    logger.info("Starting up ATA backend server...")
    from core.mongodb import get_mongo_client
    try:
        get_mongo_client().admin.command("ping")
        logger.info("✅ MongoDB Atlas connection successful")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
