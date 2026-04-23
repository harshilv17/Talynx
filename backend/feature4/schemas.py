from pydantic import BaseModel
from typing import List


class EvaluationCandidate(BaseModel):
    id: str
    name: str
    score: float
    status: str
    evaluation: dict
    decision: dict


class EvaluationResponse(BaseModel):
    job_id: str
    candidates: List[EvaluationCandidate]
