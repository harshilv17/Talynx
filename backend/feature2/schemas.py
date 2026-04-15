from pydantic import BaseModel
from typing import Optional, List


class CandidateResult(BaseModel):
    name: str
    skills: List[str]
    experience: int
    match_score: float
    resume_text: str


class StartSourcingResponse(BaseModel):
    thread_id: str
    status: str


class SourcingStatusResponse(BaseModel):
    thread_id: str
    status: str
    shortlisted_candidates: Optional[List[CandidateResult]] = None
    error_message: Optional[str] = None
