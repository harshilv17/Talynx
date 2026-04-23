from fastapi import APIRouter, HTTPException
from feature2.db_ops import get_sourcing_candidates_by_job
from feature4.schemas import EvaluationResponse, EvaluationCandidate

router = APIRouter(prefix="/api/v1/feature4", tags=["feature4"])

@router.get("/evaluation/{job_id}", response_model=EvaluationResponse)
def get_evaluation(job_id: str):
    """
    Return evaluated and decision-ready candidates for a given job.
    Includes only 'shortlisted' and 'saved' statuses.
    """
    candidates = get_sourcing_candidates_by_job(job_id)
    if not candidates:
        raise HTTPException(status_code=404, detail="No candidates found for this job ID")

    allowed_statuses = {"shortlisted", "saved"}
    filtered_candidates = []

    for cand in candidates:
        status = cand.get("status", "")
        if status in allowed_statuses:
            # Handle missing evaluation/decision gracefully
            evaluation = cand.get("evaluation") or {}
            decision = cand.get("decision") or {}
            
            filtered_candidates.append(
                EvaluationCandidate(
                    id=str(cand.get("_id", "")),
                    name=cand.get("name", ""),
                    score=float(cand.get("score", 0.0)),
                    status=status,
                    evaluation=evaluation,
                    decision=decision,
                )
            )

    return EvaluationResponse(
        job_id=job_id,
        candidates=filtered_candidates
    )
