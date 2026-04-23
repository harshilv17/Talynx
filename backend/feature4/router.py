from fastapi import APIRouter, HTTPException
from feature2.db_ops import get_sourcing_candidates_by_job, get_published_jd
from core.mongodb import get_sourcing_candidates
from bson.objectid import ObjectId
from feature4.schemas import EvaluationResponse, EvaluationCandidate, OfferResponse
from feature4.offer import generate_offer, send_offer_email

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

@router.post("/offer/{candidate_id}", response_model=OfferResponse)
def create_and_send_offer(candidate_id: str):
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID format")

    candidate = get_sourcing_candidates().find_one({"_id": oid})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    status = candidate.get("status", "")
    decision = candidate.get("decision", {})
    recommendation = decision.get("recommendation", "")

    if status not in {"shortlisted", "saved"} or recommendation != "hire":
        raise HTTPException(status_code=400, detail="Candidate is not eligible for an offer")

    job_id = candidate.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="Candidate has no associated job ID")

    jd_doc = get_published_jd(job_id)
    jd = jd_doc.get("jd_content", {}) if jd_doc else {}

    offer_text = generate_offer(candidate, jd)
    send_offer_email(candidate.get("name", "Candidate"), offer_text)

    return OfferResponse(
        success=True,
        message="Offer generated and sent",
        offer_text=offer_text
    )
