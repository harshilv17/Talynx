"""
Feature 4 evaluation + decision + offer pipeline.

Exposes two entry points:
  run_evaluation()      – evaluate a specific list of candidates
  process_candidates()  – full closed-loop automation for a job
"""
import logging

from feature1.db_ops import get_role_brief_by_thread
from feature2.db_ops import get_published_jd
from feature4.db_ops import (
    get_candidates_by_ids,
    get_candidates_for_processing,
    save_evaluation,
    mark_candidate_offered,
    mark_candidate_rejected,
)
from feature4.evaluation import compute_final_score
from feature4.decision import generate_decision
from feature4.offer import generate_offer, send_offer_email, send_rejection_email
from feature4.states import CandidateStatus, EVALUABLE_STATUSES

logger = logging.getLogger(__name__)


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _build_jd_context(job_id: str) -> dict:
    """
    Merge jd_content with role_brief fields required by the evaluator.
    """
    role_brief = get_role_brief_by_thread(job_id) or {}
    jd_doc     = get_published_jd(job_id)
    jd_content = jd_doc.get("jd_content", {}) if jd_doc else {}

    return {
        **jd_content,
        "years_of_experience": role_brief.get("years_of_experience"),
        "must_have_skills":    role_brief.get("must_have_skills", []),
    }


# ── Manual evaluation (existing flow) ─────────────────────────────────────────

def run_evaluation(
    job_id: str,
    candidate_ids: list[str],
) -> tuple[list[dict], list[dict]]:
    """
    Evaluate a specific list of candidates for the given job.

    Accepts candidates in SHORTLISTED, SAVED, or INTERVIEWED status.
    For each: scorecard → decision → persist → advance status to EVALUATED.

    Returns (evaluated_docs, errors).
    """
    jd         = _build_jd_context(job_id)
    candidates = get_candidates_by_ids(candidate_ids)

    fetched_ids = {str(c["_id"]) for c in candidates}
    not_found   = [cid for cid in candidate_ids if cid not in fetched_ids]

    evaluated: list[dict] = []
    errors: list[dict]    = [
        {"candidate_id": cid, "error": "Candidate not found"}
        for cid in not_found
    ]

    for candidate in candidates:
        cid            = str(candidate["_id"])
        current_status = candidate.get("status", "")

        try:
            current = CandidateStatus(current_status)
        except ValueError:
            errors.append({"candidate_id": cid, "error": f"Unknown status '{current_status}'"})
            continue

        if current not in EVALUABLE_STATUSES:
            errors.append({
                "candidate_id": cid,
                "error": f"Cannot evaluate candidate with status '{current_status}'. "
                         f"Must be one of: {[s.value for s in EVALUABLE_STATUSES]}",
            })
            continue

        try:
            evaluation           = compute_final_score(candidate, jd)
            candidate_with_eval  = {**candidate, "evaluation": evaluation}
            decision             = generate_decision(candidate_with_eval)

            updated = save_evaluation(cid, evaluation, decision)
            if updated:
                evaluated.append(updated)
            else:
                errors.append({"candidate_id": cid, "error": "DB update returned no document"})

        except Exception as exc:
            logger.error("Evaluation failed for candidate %s: %s", cid, exc)
            errors.append({"candidate_id": cid, "error": str(exc)})

    return evaluated, errors


# ── Automated closed-loop pipeline ────────────────────────────────────────────

def process_candidates(job_id: str) -> dict:
    """
    Full automation loop: evaluate → decide → offer or reject.

    Flow
    ----
    1. Fetch candidates where status is INTERVIEWED or EVALUATED.
    2. INTERVIEWED → run compute_final_score + generate_decision, persist.
    3. hire_high     → generate_offer, send_offer_email, mark OFFERED.
    4. hire_moderate → flag for human review (status stays EVALUATED).
    5. no_hire       → send_rejection_email, mark REJECTED.

    Idempotent: OFFERED / REJECTED candidates are excluded from the query,
    so re-running will not duplicate emails.

    Returns a summary dict with hired, rejected, pending_review, errors.
    """
    jd         = _build_jd_context(job_id)
    candidates = get_candidates_for_processing(job_id)

    hired:          list[dict] = []
    rejected:       list[dict] = []
    pending_review: list[dict] = []
    errors:         list[dict] = []

    for candidate in candidates:
        cid            = str(candidate["_id"])
        current_status = candidate.get("status", "")

        try:
            # ── Step 1: Evaluate if not already done ──────────────────────────
            if current_status == CandidateStatus.INTERVIEWED.value:
                evaluation          = compute_final_score(candidate, jd)
                candidate_with_eval = {**candidate, "evaluation": evaluation}
                decision            = generate_decision(candidate_with_eval)

                updated = save_evaluation(cid, evaluation, decision)
                if not updated:
                    raise RuntimeError("DB update returned no document during evaluation")
                candidate = updated

            # ── Step 2: Read decision ─────────────────────────────────────────
            decision_doc   = candidate.get("decision") or {}
            recommendation = decision_doc.get("recommendation", "no_hire")
            overall_score  = float((candidate.get("evaluation") or {}).get("overall_score", 0.0))
            summary_entry  = {
                "id":    cid,
                "name":  candidate.get("name", ""),
                "score": overall_score,
            }

            # ── Step 3: Act on recommendation ─────────────────────────────────
            if recommendation == "hire_high":
                offer_text = generate_offer(candidate, jd)
                try:
                    send_offer_email(candidate, offer_text)
                except Exception as email_exc:
                    logger.error(
                        "Offer email failed for %s (%s) — marking OFFERED anyway: %s",
                        cid, candidate.get("name"), email_exc,
                    )
                    errors.append({
                        "candidate_id": cid,
                        "error": f"Offer email failed (manual send required): {email_exc}",
                    })
                mark_candidate_offered(cid, offer_text)
                hired.append({**summary_entry, "tier": "hire_high"})

            elif recommendation == "hire_moderate":
                pending_review.append({**summary_entry, "tier": "hire_moderate"})
                logger.info("Candidate %s flagged for manual review (hire_moderate)", cid)

            else:  # no_hire
                try:
                    send_rejection_email(candidate)
                except Exception as email_exc:
                    logger.warning(
                        "Rejection email failed for %s (%s) — marking rejected anyway: %s",
                        cid, candidate.get("name"), email_exc,
                    )
                    errors.append({
                        "candidate_id": cid,
                        "error": f"Rejection email failed: {email_exc}",
                    })
                mark_candidate_rejected(cid)
                rejected.append(summary_entry)

        except Exception as exc:
            logger.error("Pipeline processing failed for candidate %s: %s", cid, exc)
            errors.append({"candidate_id": cid, "error": str(exc)})

    return {
        "job_id":          job_id,
        "total_processed": len(candidates),
        "hired":           hired,
        "rejected":        rejected,
        "pending_review":  pending_review,
        "errors":          errors,
    }
