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


class StartSourcingResponse(BaseModel):
    thread_id: str
    status: str


class SourcingStatusResponse(BaseModel):
    thread_id: str
    status: str
    error_message: Optional[str] = None


class SourcingCandidatesResponse(BaseModel):
    job_id: str
    candidates: List[CandidateResult]


class CandidateActionResponse(BaseModel):
    success: bool
    new_status: str
    message: str
