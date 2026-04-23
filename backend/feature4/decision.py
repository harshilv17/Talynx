"""Feature 4 – Phase 2: Hire / No-Hire Decision Engine.

Produces a deterministic hire recommendation, confidence score, and
human-readable reason for every candidate, based solely on the Phase 1
evaluation scorecard and the candidate's screening status.
"""


# ── Thresholds ────────────────────────────────────────────────────────────────
_HIRE_HIGH_THRESHOLD   = 75.0   # overall_score >= this → hire, high confidence
_HIRE_MEDIUM_THRESHOLD = 50.0   # overall_score >= this → hire, moderate confidence
                                 # overall_score <  this → no_hire


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


def _confidence(overall_score: float) -> float:
    """
    Derive confidence directly from the overall score.

    overall_score is in [0, 100]; we normalise to [0, 1] and clamp for safety.
    """
    return _clamp(overall_score / 100.0)


def _reason(recommendation: str, overall_score: float, status: str) -> str:
    """
    Return a concise, deterministic explanation for the decision.

    The logic mirrors the recommendation tiers so the text is always
    consistent with the outcome.
    """
    if status == "rejected":
        return (
            "Candidate was rejected during screening due to unmet minimum "
            "requirements (experience or must-have skills)."
        )

    if recommendation == "hire":
        if overall_score >= _HIRE_HIGH_THRESHOLD:
            return (
                "Strong technical and skill match with sufficient experience. "
                "Candidate meets or exceeds all key criteria."
            )
        # hire but below high threshold → moderate band
        return (
            "Moderate alignment across criteria. Candidate clears the minimum "
            "bar but has some skill or experience gaps worth exploring."
        )

    # no_hire path
    return (
        "Insufficient match across required criteria. "
        "Candidate scores below acceptable thresholds in one or more dimensions."
    )


def generate_decision(candidate: dict) -> dict:
    """
    Generate a hire / no-hire decision for *candidate*.

    Parameters
    ----------
    candidate : dict
        Candidate document.  Must contain ``status`` and, ideally,
        ``evaluation.overall_score``.  Missing fields are handled safely.

    Returns
    -------
    dict with keys:
        recommendation – "hire" | "no_hire"
        confidence     – float in [0, 1]
        reason         – str
    """
    status: str = candidate.get("status") or ""

    # Safely retrieve the overall score from the Phase 1 scorecard.
    evaluation = candidate.get("evaluation") or {}
    try:
        overall_score = float(evaluation.get("overall_score") or 0.0)
    except (TypeError, ValueError):
        overall_score = 0.0

    overall_score = _clamp(overall_score, 0.0, 100.0)

    # ── Decision rules ────────────────────────────────────────────────────────
    if status == "rejected":
        recommendation = "no_hire"
    elif overall_score >= _HIRE_HIGH_THRESHOLD:
        recommendation = "hire"
    elif overall_score >= _HIRE_MEDIUM_THRESHOLD:
        recommendation = "hire"   # low-confidence hire
    else:
        recommendation = "no_hire"

    confidence = _confidence(overall_score)
    reason     = _reason(recommendation, overall_score, status)

    return {
        "recommendation": recommendation,
        "confidence":     round(confidence, 4),
        "reason":         reason,
    }
