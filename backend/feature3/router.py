import logging
from fastapi import APIRouter, HTTPException

from feature3.pipeline import run_outreach, run_outreach_retry
from feature3.email_generator import generate_outreach_email
from feature3.schemas import (
    OutreachRequest, OutreachResponse, OutreachSuccess, OutreachFailure,
    RetryRequest,
    EmailPreviewRequest, EmailPreviewResponse,
)
from feature4.db_ops import get_candidate_by_id
from feature2.db_ops import get_published_jd
from feature1.db_ops import get_role_brief_by_thread

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/feature3", tags=["feature3"])


# ── POST /outreach ─────────────────────────────────────────────────────────────

@router.post("/outreach", response_model=OutreachResponse)
def send_outreach(request: OutreachRequest):
    """
    Generate and send personalized outreach emails to a list of candidates.

    Each entry in `candidates` must include:
      - candidate_id : MongoDB _id of the sourcing_candidates document
      - email        : destination email address for this candidate

    Candidates must be in SHORTLISTED, SAVED, or EVALUATED status.
    The endpoint processes every candidate and never fails the whole batch —
    per-candidate errors are returned in the `failed` list.
    """
    if not request.candidates:
        raise HTTPException(status_code=400, detail="At least one candidate is required")

    targets = [
        {"candidate_id": c.candidate_id, "email": c.email}
        for c in request.candidates
    ]

    successes, failures = run_outreach(request.job_id, targets)

    return OutreachResponse(
        job_id=request.job_id,
        sent=[OutreachSuccess(**s) for s in successes],
        failed=[OutreachFailure(**f) for f in failures],
        total=len(request.candidates),
        sent_count=len(successes),
        failed_count=len(failures),
    )


# ── POST /outreach/retry ───────────────────────────────────────────────────────

@router.post("/outreach/retry", response_model=OutreachResponse)
def retry_outreach(request: RetryRequest):
    """
    Retry sending emails for all candidates in a job whose previous outreach failed.

    Re-uses the stored subject + body — no LLM call is made.
    Only the email delivery step is retried.
    """
    successes, failures = run_outreach_retry(request.job_id)

    if not successes and not failures:
        raise HTTPException(
            status_code=404,
            detail="No failed outreach records found for this job",
        )

    return OutreachResponse(
        job_id=request.job_id,
        sent=[OutreachSuccess(**s) for s in successes],
        failed=[OutreachFailure(**f) for f in failures],
        total=len(successes) + len(failures),
        sent_count=len(successes),
        failed_count=len(failures),
    )


# ── POST /outreach/preview ─────────────────────────────────────────────────────

@router.post("/outreach/preview", response_model=EmailPreviewResponse)
def preview_outreach_email(request: EmailPreviewRequest):
    """
    Generate and return a personalized outreach email for a candidate
    WITHOUT sending it or updating any state.

    Useful for recruiters to review the draft before triggering bulk outreach.
    """
    candidate = get_candidate_by_id(request.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    role_brief = get_role_brief_by_thread(request.job_id) or {}
    jd_doc     = get_published_jd(request.job_id)
    jd_content = jd_doc.get("jd_content", {}) if jd_doc else {}
    jd = {
        **jd_content,
        "must_have_skills":    role_brief.get("must_have_skills", []),
        "years_of_experience": role_brief.get("years_of_experience"),
    }

    try:
        email_content = generate_outreach_email(candidate, jd)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Email generation failed: {exc}")

    return EmailPreviewResponse(
        candidate_id=request.candidate_id,
        name=candidate.get("name", ""),
        subject=email_content["subject"],
        body=email_content["body"],
    )
