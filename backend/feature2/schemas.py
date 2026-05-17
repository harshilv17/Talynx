from pydantic import BaseModel
from typing import Optional, List


class CandidateResult(BaseModel):
    id: str  # mapped from _id
    name: str
    skills: List[str]
    experience: float
    score: float
    status: str
    rejection_reason: Optional[str] = None
    resume_text: str
    source: Optional[str] = "github"
    response: Optional[str] = None
    evaluation: Optional[dict] = None
    notes: Optional[str] = None
    rejection_feedback: Optional[dict] = None


class StartSourcingResponse(BaseModel):
    thread_id: str
    status: str


class SourcingStatusResponse(BaseModel):
    thread_id: str
    status: str
    stage: Optional[str] = None
    progress: Optional[int] = 0
    message: Optional[str] = None
    error_message: Optional[str] = None
    elapsed_seconds: Optional[int] = 0


class SourcingCandidatesResponse(BaseModel):
    job_id: str
    candidates: List[CandidateResult]


class CandidateActionResponse(BaseModel):
    success: bool
    new_status: str
    message: str

class CandidateActionRequest(BaseModel):
    status: str
