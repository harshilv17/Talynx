"""
Feature 3 — Outreach pipeline.

For each (candidate_id, email) pair:
  1. Fetch candidate from DB.
  2. Validate status is contactable.
  3. Fetch JD context (jd_content + role_brief fields).
  4. Generate personalized email via Groq.
  5. Send email via configured provider.
  6. Persist outreach record + advance status → CONTACTED   (on success)
     OR persist failed record + leave status unchanged      (on failure).

Returns (successes, failures) — never raises; all errors are per-candidate.
"""
import logging

from feature1.db_ops import get_role_brief_by_thread
from feature2.db_ops import get_published_jd
from feature4.db_ops import get_candidates_by_ids
from feature4.states import CandidateStatus, CONTACTABLE_STATUSES
from feature3.email_generator import generate_outreach_email
from feature3.email_sender import send_email
from feature3 import db_ops

logger = logging.getLogger(__name__)


def _build_jd_context(job_id: str) -> dict:
    """Merge jd_content with role_brief fields needed by the email generator."""
    role_brief = get_role_brief_by_thread(job_id) or {}
    jd_doc     = get_published_jd(job_id)
    jd_content = jd_doc.get("jd_content", {}) if jd_doc else {}
    return {
        **jd_content,
        "must_have_skills":   role_brief.get("must_have_skills", []),
        "years_of_experience": role_brief.get("years_of_experience"),
    }


def run_outreach(
    job_id: str,
    targets: list[dict],        # each: {"candidate_id": str, "email": str}
) -> tuple[list[dict], list[dict]]:
    """
    Execute the outreach pipeline for a list of candidates.

    Parameters
    ----------
    job_id  : thread_id of the published JD
    targets : list of {candidate_id, email}

    Returns
    -------
    successes : list[dict]  — {candidate_id, name, email, subject}
    failures  : list[dict]  — {candidate_id, email, error}
    """
    jd = _build_jd_context(job_id)

    candidate_ids = [t["candidate_id"] for t in targets]
    email_map     = {t["candidate_id"]: t["email"] for t in targets}
    candidates    = get_candidates_by_ids(candidate_ids)
    fetched_ids   = {str(c["_id"]) for c in candidates}

    successes: list[dict] = []
    failures:  list[dict] = []

    # Report any IDs that don't exist in DB
    for cid in candidate_ids:
        if cid not in fetched_ids:
            failures.append({"candidate_id": cid, "email": email_map.get(cid, ""), "error": "Candidate not found"})

    for candidate in candidates:
        cid   = str(candidate["_id"])
        email = email_map.get(cid, "").strip()
        name  = candidate.get("name", "")

        # ── Validate email address ────────────────────────────────────────
        if not email or "@" not in email:
            failures.append({"candidate_id": cid, "email": email, "error": "Invalid or missing email address"})
            continue

        # ── Validate state machine transition ─────────────────────────────
        current_status = candidate.get("status", "")
        try:
            if CandidateStatus(current_status) not in CONTACTABLE_STATUSES:
                failures.append({
                    "candidate_id": cid,
                    "email": email,
                    "error": f"Cannot contact candidate with status '{current_status}'. "
                             f"Must be one of: {[s.value for s in CONTACTABLE_STATUSES]}",
                })
                continue
        except ValueError:
            failures.append({"candidate_id": cid, "email": email, "error": f"Unknown candidate status '{current_status}'"})
            continue

        # ── Generate email ────────────────────────────────────────────────
        try:
            email_content = generate_outreach_email(candidate, jd)
            subject = email_content["subject"]
            body    = email_content["body"]
        except Exception as exc:
            error_msg = f"Email generation failed: {exc}"
            logger.error("[Outreach] %s for candidate %s", error_msg, cid)
            db_ops.save_outreach_failure(cid, email, "", "", error_msg)
            failures.append({"candidate_id": cid, "email": email, "error": error_msg})
            continue

        # ── Send email ────────────────────────────────────────────────────
        try:
            send_email(email, subject, body)
        except Exception as exc:
            error_msg = f"Email delivery failed: {exc}"
            logger.error("[Outreach] %s for candidate %s (%s)", error_msg, cid, name)
            # Store the generated content so it can be retried
            db_ops.save_outreach_failure(cid, email, subject, body, error_msg)
            failures.append({"candidate_id": cid, "email": email, "error": error_msg})
            continue

        # ── Persist success ───────────────────────────────────────────────
        db_ops.save_outreach_success(cid, email, subject, body)
        logger.info("[Outreach] Sent to %s (%s)", name, email)
        successes.append({"candidate_id": cid, "name": name, "email": email, "subject": subject})

    return successes, failures


def run_outreach_retry(job_id: str) -> tuple[list[dict], list[dict]]:
    """
    Retry all candidates for a job whose last outreach attempt failed.

    Uses the previously generated subject + body so no LLM call is made.
    Only re-attempts the email send step.
    """
    failed_candidates = db_ops.get_candidates_with_failed_outreach(job_id)
    if not failed_candidates:
        return [], []

    successes: list[dict] = []
    failures:  list[dict] = []

    for candidate in failed_candidates:
        cid     = str(candidate["_id"])
        name    = candidate.get("name", "")
        outreach = candidate.get("outreach", {})
        email   = outreach.get("email_address", "")
        subject = outreach.get("email_subject", "")
        body    = outreach.get("email_body", "")

        if not email or "@" not in email:
            failures.append({"candidate_id": cid, "email": email, "error": "No valid email stored for retry"})
            continue

        if not subject or not body:
            failures.append({"candidate_id": cid, "email": email, "error": "No email content stored; run full outreach instead"})
            continue

        try:
            send_email(email, subject, body)
        except Exception as exc:
            error_msg = f"Retry delivery failed: {exc}"
            logger.error("[Outreach Retry] %s for candidate %s", error_msg, cid)
            db_ops.save_outreach_failure(cid, email, subject, body, error_msg)
            failures.append({"candidate_id": cid, "email": email, "error": error_msg})
            continue

        db_ops.save_outreach_success(cid, email, subject, body)
        logger.info("[Outreach Retry] Re-sent to %s (%s)", name, email)
        successes.append({"candidate_id": cid, "name": name, "email": email, "subject": subject})

    return successes, failures
