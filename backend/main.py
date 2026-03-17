from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from feature1.router import router as feature1_router

app = FastAPI(
    title="ATA - Autonomous Talent Acquisition",
    description="AI-powered hiring automation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feature1_router)


@app.get("/")
def root():
    return {
        "message": "ATA API is running",
        "version": "1.0.0",
        "features": ["feature1"]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
