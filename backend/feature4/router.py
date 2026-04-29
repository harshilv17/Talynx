import logging
from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from pydantic import BaseModel

from core.mongodb import get_sourcing_candidates
from feature2.db_ops import get_sourcing_candidates_by_job, get_published_jd
from feature4.pipeline import run_evaluation, process_candidates
from feature4.offer import generate_offer, send_offer_email, _compute_salary
from feature4.db_ops import mark_candidate_offered
from feature4.states import CandidateStatus
from feature4.schemas import (
    EvaluateRequest, EvaluateResponse, EvaluatedCandidate,
    EvaluationScores, DecisionResult,
    EvaluationResponse, EvaluationCandidate,
    OfferResponse,
    ProcessRequest, ProcessResponse, ProcessedCandidate,
)

logger = logging.getLogger(__name__)

router          = APIRouter(prefix="/api/v1/feature4",    tags=["feature4"])
candidates_router = APIRouter(prefix="/api/v1/candidates", tags=["candidates"])

_HIRE_RECOMMENDATIONS = {"hire_high", "hire_moderate"}


# ── POST /feature4/evaluate ───────────────────────────────────────────────────

@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_candidates(request: EvaluateRequest):
    """
    Evaluate a list of shortlisted / saved / interviewed candidates for a job.

    For each candidate_id:
      - validates status is SHORTLISTED, SAVED, or INTERVIEWED
      - runs evaluation scorecard (compute_final_score)
      - runs hire/no-hire decision (generate_decision)
      - persists both to DB
      - advances status → EVALUATED
    """
    if not request.candidate_ids:
        raise HTTPException(status_code=400, detail="At least one candidate_id is required")

    evaluated_docs, errors = run_evaluation(request.job_id, request.candidate_ids)

    result: list[EvaluatedCandidate] = []
    for c in evaluated_docs:
        eval_data = c.get("evaluation", {})
        dec_data  = c.get("decision", {})
        try:
            result.append(EvaluatedCandidate(
                id=str(c["_id"]),
                name=c.get("name", ""),
                score=float(c.get("score", 0.0)),
                status=c.get("status", ""),
                evaluation=EvaluationScores(**eval_data),
                decision=DecisionResult(
                    recommendation=dec_data.get("recommendation", "no_hire"),
                    confidence=float(dec_data.get("confidence", 0.0)),
                    reason=dec_data.get("reason", ""),
                ),
            ))
        except Exception as exc:
            logger.error("Failed to serialise evaluated candidate %s: %s", c.get("_id"), exc)
            errors.append({"candidate_id": str(c.get("_id", "")), "error": str(exc)})

    return EvaluateResponse(job_id=request.job_id, evaluated=result, errors=errors)


# ── GET /feature4/evaluation/{job_id} ────────────────────────────────────────

@router.get("/evaluation/{job_id}", response_model=EvaluationResponse)
def get_evaluation(job_id: str):
    """Return all EVALUATED candidates for a job, with their scorecards and decisions."""
    all_candidates = get_sourcing_candidates_by_job(job_id)
    if not all_candidates:
        raise HTTPException(status_code=404, detail="No candidates found for this job ID")

    evaluated = [
        c for c in all_candidates
        if c.get("status") == CandidateStatus.EVALUATED
    ]

    result: list[EvaluationCandidate] = []
    for cand in evaluated:
        eval_data = cand.get("evaluation")
        dec_data  = cand.get("decision")

        result.append(EvaluationCandidate(
            id=str(cand["_id"]),
            name=cand.get("name", ""),
            score=float(cand.get("score", 0.0)),
            status=cand["status"],
            evaluation=EvaluationScores(**eval_data) if eval_data else None,
            decision=DecisionResult(**dec_data)       if dec_data  else None,
        ))

    return EvaluationResponse(job_id=job_id, candidates=result)


class GenerateOfferRequest(BaseModel):
    candidate_id: str
    jd_id: str

@router.post("/generate-offer")
def api_generate_offer(request: GenerateOfferRequest):
    """Generate an offer letter preview for a candidate."""
    try:
        oid = ObjectId(request.candidate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")

    candidate = get_sourcing_candidates().find_one({"_id": oid})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if candidate.get("response") != "Interested":
        raise HTTPException(
            status_code=400, 
            detail="Cannot generate offer for candidate who is not interested"
        )

    jd_doc = get_published_jd(request.jd_id)
    jd = jd_doc.get("jd_content", {}) if jd_doc else {}
    
    role = jd.get("job_title", "Software Engineer")
    
    evaluation = candidate.get("evaluation", {})
    overall_score = float(evaluation.get("overall_score", 0.0))
    salary = _compute_salary(overall_score, jd)
    
    name = candidate.get("name", "Candidate")
    
    # Simple offer template
    offer_text = f"Dear {name},\n\nWe are pleased to offer you the position of {role} at our company.\n\nBased on your experience and evaluation, we are offering a compensation of {salary}.\n\nWe look forward to having you on our team.\n\nBest regards,\nHR Team"
    
    return {
        "offer_text": offer_text,
        "candidate_name": name,
        "role": role,
        "salary": salary
    }

# ── POST /feature4/offer/{candidate_id} ──────────────────────────────────────

@router.post("/offer/{candidate_id}", response_model=OfferResponse)
def create_and_send_offer(candidate_id: str):
    """
    Generate and send an offer letter for an EVALUATED candidate
    whose decision is hire_high or hire_moderate.
    """
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")

    candidate = get_sourcing_candidates().find_one({"_id": oid})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if candidate.get("status") not in {CandidateStatus.EVALUATED.value, CandidateStatus.RESPONDED.value}:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Candidate must be in 'evaluated' or 'responded' status to receive an offer "
                f"(current: '{candidate.get('status')}')."
            ),
        )

    if candidate.get("response") != "Interested":
        raise HTTPException(
            status_code=400, 
            detail="Cannot generate offer for candidate who is not interested"
        )

    # HR can override AI decision, so we don't block on recommendation
    # decision = candidate.get("decision") or {}
    # if decision.get("recommendation") not in _HIRE_RECOMMENDATIONS:
    #     logger.warning("HR generating offer despite AI recommendation: %s", decision.get("recommendation"))

    job_id    = candidate.get("job_id")
    jd_doc    = get_published_jd(job_id) if job_id else None
    jd        = jd_doc.get("jd_content", {}) if jd_doc else {}

    offer_text = generate_offer(candidate, jd)

    try:
        send_offer_email(candidate, offer_text)
        from feature4.db_ops import mark_candidate_hired
        mark_candidate_hired(candidate_id)
    except Exception as exc:
        logger.error("Failed to send offer email for candidate %s: %s", candidate_id, exc)
        raise HTTPException(status_code=502, detail=f"Email delivery failed: {exc}")

    return OfferResponse(success=True, message="Offer generated and sent", offer_text=offer_text)


# ── POST /candidates/process ──────────────────────────────────────────────────

@candidates_router.post("/process", response_model=ProcessResponse)
def process_job_candidates(request: ProcessRequest):
    """
    Full autonomous pipeline: evaluate → decide → offer or reject.

    Fetches all INTERVIEWED and EVALUATED candidates for the given job and:
      - Evaluates INTERVIEWED candidates (scorecard + decision)
      - Sends offer email to hire_high candidates → status OFFERED
      - Flags hire_moderate candidates for human review (status stays EVALUATED)
      - Sends rejection email to no_hire candidates → status REJECTED

    Idempotent — running twice won't duplicate emails because OFFERED/REJECTED
    candidates are excluded from the processing query.
    """
    if not request.job_id:
        raise HTTPException(status_code=400, detail="job_id is required")

    summary = process_candidates(request.job_id)

    return ProcessResponse(
        job_id          = summary["job_id"],
        total_processed = summary["total_processed"],
        hired           = [ProcessedCandidate(**c) for c in summary["hired"]],
        rejected        = [ProcessedCandidate(**c) for c in summary["rejected"]],
        pending_review  = [ProcessedCandidate(**c) for c in summary["pending_review"]],
        errors          = summary["errors"],
    )
