"""FastAPI endpoints for RAG-based rejection feedback."""
import logging
from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId

from core.mongodb import get_sourcing_candidates
from feature2.db_ops import get_published_jd
from feature1.db_ops import get_role_brief_by_thread
from feature4.feedback.generator import generate_rejection_feedback
from feature4.feedback import db_ops as feedback_db
from feature4.feedback.schemas import (
    FeedbackResponse, FeedbackListResponse,
    FeedbackListItem, SendFeedbackResponse, RejectionFeedback,
    SkillGap, RAGMetadata,
    BulkFeedbackGenerateResponse, BulkFeedbackSendResponse, BulkResultError,
)
from feature3.email_sender import send_email

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/feature4/feedback",
    tags=["feedback"],
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_candidate_or_404(candidate_id: str) -> dict:
    try:
        oid = ObjectId(candidate_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid candidate ID")
    doc = get_sourcing_candidates().find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return doc


def _assert_rejected(candidate: dict):
    """Only rejected candidates should receive feedback."""
    status = candidate.get("status", "")
    response = candidate.get("response", "")

    if status != "rejected":
        raise HTTPException(
            status_code=400,
            detail=f"Feedback is only for rejected candidates (current status: '{status}')",
        )
    # Candidates who responded "Not Interested" should not get rejection feedback
    if response == "Not Interested":
        raise HTTPException(
            status_code=400,
            detail="Candidate declined the opportunity — rejection feedback not applicable",
        )


def _build_feedback_response(candidate_id: str, name: str, fb: dict) -> FeedbackResponse:
    """Map raw MongoDB feedback dict to a typed Pydantic response."""
    skill_gaps = [
        SkillGap(**sg) if isinstance(sg, dict) else SkillGap(skill=str(sg), importance="unknown", recommendation="")
        for sg in fb.get("skill_gaps", [])
    ]
    rag = fb.get("rag_metadata", {})

    return FeedbackResponse(
        success=True,
        candidate_id=candidate_id,
        candidate_name=name,
        feedback=RejectionFeedback(
            feedback_id=fb.get("feedback_id", ""),
            generated_at=fb.get("generated_at"),
            model_used=fb.get("model_used", ""),
            version=fb.get("version", 1),
            strengths=fb.get("strengths", []),
            skill_gaps=skill_gaps,
            experience_gaps=fb.get("experience_gaps", []),
            improvement_suggestions=fb.get("improvement_suggestions", []),
            technologies_to_learn=fb.get("technologies_to_learn", []),
            overall_summary=fb.get("overall_summary", ""),
            encouragement=fb.get("encouragement", ""),
            rag_metadata=RAGMetadata(**rag) if rag else RAGMetadata(
                chunks_used=0, retrieval_scores=[], embedding_model="", total_chunks=0
            ),
            email_sent=fb.get("email_sent", False),
            email_sent_at=fb.get("email_sent_at"),
        ),
    )


# ── POST /generate ────────────────────────────────────────────────────────────

@router.post("/{candidate_id}/generate", response_model=FeedbackResponse)
def generate_feedback(candidate_id: str):
    """Generate RAG-based personalized rejection feedback."""
    candidate = _get_candidate_or_404(candidate_id)
    _assert_rejected(candidate)

    # Don't regenerate if feedback already exists (use /regenerate instead)
    if candidate.get("rejection_feedback"):
        raise HTTPException(
            status_code=400,
            detail="Feedback already exists. Use /regenerate to create a new version.",
        )

    job_id = candidate.get("job_id", "")
    jd_doc = get_published_jd(job_id)
    jd_content = jd_doc.get("jd_content", {}) if jd_doc else {}
    role_brief = get_role_brief_by_thread(job_id)

    feedback = generate_rejection_feedback(
        candidate=candidate,
        jd_content=jd_content,
        role_brief=role_brief,
        version=1,
    )

    updated = feedback_db.save_feedback(candidate_id, feedback)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to save feedback")

    return _build_feedback_response(candidate_id, candidate.get("name", ""), feedback)


# ── POST /regenerate ──────────────────────────────────────────────────────────

@router.post("/{candidate_id}/regenerate", response_model=FeedbackResponse)
def regenerate_feedback(candidate_id: str):
    """Regenerate feedback with incremented version."""
    candidate = _get_candidate_or_404(candidate_id)
    _assert_rejected(candidate)

    existing = candidate.get("rejection_feedback", {})
    new_version = existing.get("version", 0) + 1

    job_id = candidate.get("job_id", "")
    jd_doc = get_published_jd(job_id)
    jd_content = jd_doc.get("jd_content", {}) if jd_doc else {}
    role_brief = get_role_brief_by_thread(job_id)

    feedback = generate_rejection_feedback(
        candidate=candidate,
        jd_content=jd_content,
        role_brief=role_brief,
        version=new_version,
    )

    updated = feedback_db.save_feedback(candidate_id, feedback)
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to save feedback")

    return _build_feedback_response(candidate_id, candidate.get("name", ""), feedback)


# ── GET /fetch ────────────────────────────────────────────────────────────────

@router.get("/{candidate_id}", response_model=FeedbackResponse)
def fetch_feedback(candidate_id: str):
    """Retrieve stored feedback for a candidate."""
    doc = feedback_db.get_feedback(candidate_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Candidate not found")

    fb = doc.get("rejection_feedback")
    if not fb:
        raise HTTPException(status_code=404, detail="No feedback generated yet")

    return _build_feedback_response(candidate_id, doc.get("name", ""), fb)


# ── POST /send ────────────────────────────────────────────────────────────────

@router.post("/{candidate_id}/send", response_model=SendFeedbackResponse)
def send_feedback_email(candidate_id: str):
    """Send the generated feedback to the candidate via email."""
    candidate = _get_candidate_or_404(candidate_id)
    fb = candidate.get("rejection_feedback")
    if not fb:
        raise HTTPException(status_code=400, detail="No feedback to send. Generate first.")

    email = (
        candidate.get("email")
        or (candidate.get("outreach") or {}).get("email_address")
    )
    name = candidate.get("name", "Candidate")

    # Build email body from feedback
    body_parts = [
        f"Dear {name},\n",
        "Thank you for your interest in the position and the time you invested in our process.\n",
        f"{fb.get('overall_summary', '')}\n",
        "── Your Strengths ──",
    ]
    for s in fb.get("strengths", []):
        body_parts.append(f"  • {s}")

    gaps = fb.get("skill_gaps", [])
    if gaps:
        body_parts.append("\n── Areas for Growth ──")
        for g in gaps:
            if isinstance(g, dict):
                body_parts.append(f"  • {g.get('skill', '')}: {g.get('recommendation', '')}")

    suggestions = fb.get("improvement_suggestions", [])
    if suggestions:
        body_parts.append("\n── Suggestions ──")
        for s in suggestions:
            body_parts.append(f"  • {s}")

    body_parts.append(f"\n{fb.get('encouragement', '')}")
    body_parts.append("\nWarm regards,\nTalent Acquisition Team\nTalynx AI")

    body = "\n".join(body_parts)
    subject = f"Feedback on Your Application — {name}"

    if not email:
        logger.warning("No email for candidate '%s'. Mocking send.", name)
        feedback_db.mark_feedback_sent(candidate_id)
        return SendFeedbackResponse(success=True, message="Feedback sent (mock — no email on file)", candidate_id=candidate_id)

    try:
        send_email(email, subject, body)
        feedback_db.mark_feedback_sent(candidate_id)
        return SendFeedbackResponse(success=True, message="Feedback email sent", candidate_id=candidate_id)
    except Exception as e:
        logger.error("Failed to send feedback email: %s", e)
        raise HTTPException(status_code=502, detail=f"Email delivery failed: {e}")


# ── GET /job/{job_id} ─────────────────────────────────────────────────────────

@router.get("/job/{job_id}", response_model=FeedbackListResponse)
def list_feedback_for_job(job_id: str):
    """List all candidates with feedback for a given job."""
    docs = feedback_db.get_all_feedback_for_job(job_id)

    items = []
    for doc in docs:
        fb = doc.get("rejection_feedback", {})
        items.append(FeedbackListItem(
            candidate_id=str(doc["_id"]),
            candidate_name=doc.get("name", ""),
            status=doc.get("status", ""),
            feedback_version=fb.get("version", 1),
            generated_at=fb.get("generated_at"),
            email_sent=fb.get("email_sent", False),
        ))

    return FeedbackListResponse(job_id=job_id, total=len(items), feedbacks=items)

# ── POST /job/{job_id}/generate-all ───────────────────────────────────────────

@router.post("/job/{job_id}/generate-all", response_model=BulkFeedbackGenerateResponse)
def generate_all_feedback(job_id: str, force_regenerate: bool = False):
    """Generate feedback for all rejected candidates for a job."""
    from feature2.db_ops import get_sourcing_candidates_by_job
    candidates = get_sourcing_candidates_by_job(job_id)

    jd_doc = get_published_jd(job_id)
    jd_content = jd_doc.get("jd_content", {}) if jd_doc else {}
    role_brief = get_role_brief_by_thread(job_id)

    success_count = 0
    failure_count = 0
    errors = []
    processed = 0

    for candidate in candidates:
        status = candidate.get("status", "")
        response = candidate.get("response", "")

        if status != "rejected" or response == "Not Interested":
            continue

        processed += 1
        candidate_id = str(candidate["_id"])
        name = candidate.get("name", "Unknown")

        existing = candidate.get("rejection_feedback")
        if existing and not force_regenerate:
            continue  # skip already generated

        try:
            version = existing.get("version", 0) + 1 if existing else 1
            feedback = generate_rejection_feedback(
                candidate=candidate,
                jd_content=jd_content,
                role_brief=role_brief,
                version=version,
            )
            feedback_db.save_feedback(candidate_id, feedback)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to generate feedback for {name}: {e}")
            failure_count += 1
            errors.append(BulkResultError(candidate_id=candidate_id, candidate_name=name, error=str(e)))

    return BulkFeedbackGenerateResponse(
        success=True,
        job_id=job_id,
        total_processed=processed,
        success_count=success_count,
        failure_count=failure_count,
        errors=errors
    )

# ── POST /job/{job_id}/send-all ───────────────────────────────────────────────

@router.post("/job/{job_id}/send-all", response_model=BulkFeedbackSendResponse)
def send_all_feedback(job_id: str):
    """Send emails for all rejected candidates with generated feedback."""
    from feature2.db_ops import get_sourcing_candidates_by_job
    candidates = get_sourcing_candidates_by_job(job_id)

    success_count = 0
    failure_count = 0
    errors = []
    processed = 0

    for candidate in candidates:
        status = candidate.get("status", "")
        response = candidate.get("response", "")

        if status != "rejected" or response == "Not Interested":
            continue

        fb = candidate.get("rejection_feedback")
        if not fb:
            continue

        if fb.get("email_sent"):
            continue

        processed += 1
        candidate_id = str(candidate["_id"])
        name = candidate.get("name", "Unknown")
        email_address = (candidate.get("email") or (candidate.get("outreach") or {}).get("email_address"))

        # Build email body
        body_parts = [
            f"Dear {name},\n",
            "Thank you for your interest in the position and the time you invested in our process.\n",
            f"{fb.get('overall_summary', '')}\n",
            "── Your Strengths ──",
        ]
        for s in fb.get("strengths", []):
            body_parts.append(f"  • {s}")

        gaps = fb.get("skill_gaps", [])
        if gaps:
            body_parts.append("\n── Areas for Growth ──")
            for g in gaps:
                if isinstance(g, dict):
                    body_parts.append(f"  • {g.get('skill', '')}: {g.get('recommendation', '')}")

        suggestions = fb.get("improvement_suggestions", [])
        if suggestions:
            body_parts.append("\n── Suggestions ──")
            for s in suggestions:
                body_parts.append(f"  • {s}")

        body_parts.append(f"\n{fb.get('encouragement', '')}")
        body_parts.append("\nWarm regards,\nTalent Acquisition Team\nTalynx AI")

        body = "\n".join(body_parts)
        subject = f"Feedback on Your Application — {name}"

        if not email_address:
            logger.warning("No email for candidate '%s'. Mocking send.", name)
            feedback_db.mark_feedback_sent(candidate_id)
            success_count += 1
            continue

        try:
            send_email(email_address, subject, body)
            feedback_db.mark_feedback_sent(candidate_id)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send feedback email to {name}: {e}")
            failure_count += 1
            errors.append(BulkResultError(candidate_id=candidate_id, candidate_name=name, error=str(e)))

    return BulkFeedbackSendResponse(
        success=True,
        job_id=job_id,
        total_processed=processed,
        success_count=success_count,
        failure_count=failure_count,
        errors=errors
    )
