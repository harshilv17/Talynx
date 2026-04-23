from pydantic import BaseModel
from typing import List, Optional


# ── Evaluation scorecard ──────────────────────────────────────────────────────

class EvaluationScores(BaseModel):
    technical_score:   float
    experience_score:  float
    skill_match_score: float
    interview_score:   Optional[float] = 0.0   # 0 when no interview data recorded
    overall_score:     float
    summary:           str


# ── Hire / no-hire decision ───────────────────────────────────────────────────

class DecisionResult(BaseModel):
    recommendation: str   # "hire_high" | "hire_moderate" | "no_hire"
    confidence:     float
    reason:         str


# ── POST /evaluate ────────────────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    job_id:        str
    candidate_ids: List[str]


class EvaluatedCandidate(BaseModel):
    id:         str
    name:       str
    score:      float        # original cosine-similarity score from sourcing
    status:     str
    evaluation: EvaluationScores
    decision:   DecisionResult


class EvaluateResponse(BaseModel):
    job_id:    str
    evaluated: List[EvaluatedCandidate]
    errors:    List[dict]


# ── GET /evaluation/{job_id} ──────────────────────────────────────────────────

class EvaluationCandidate(BaseModel):
    id:         str
    name:       str
    score:      float
    status:     str
    evaluation: Optional[EvaluationScores] = None
    decision:   Optional[DecisionResult]   = None


class EvaluationResponse(BaseModel):
    job_id:     str
    candidates: List[EvaluationCandidate]


# ── POST /offer/{candidate_id} ────────────────────────────────────────────────

class OfferResponse(BaseModel):
    success:    bool
    message:    str
    offer_text: str


# ── POST /candidates/process ──────────────────────────────────────────────────

class ProcessRequest(BaseModel):
    job_id: str


class ProcessedCandidate(BaseModel):
    id:    str
    name:  str
    score: float
    tier:  Optional[str] = None   # "hire_high" | "hire_moderate" | None


class ProcessResponse(BaseModel):
    job_id:          str
    total_processed: int
    hired:           List[ProcessedCandidate]
    rejected:        List[ProcessedCandidate]
    pending_review:  List[ProcessedCandidate]
    errors:          List[dict]
