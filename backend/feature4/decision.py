"""Feature 4 – Phase 2: Hire / No-Hire Decision Engine.

Produces a deterministic hire recommendation, confidence score, and
human-readable reason based on the Phase 1 evaluation scorecard.

Recommendations:
  hire_high     – overall_score >= 75  (strong, send offer automatically)
  hire_moderate – 50 <= score < 75     (borderline, flag for human review)
  no_hire       – score < 50           (reject)
"""

_HIRE_HIGH_THRESHOLD   = 75.0
_HIRE_MEDIUM_THRESHOLD = 50.0


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _confidence(overall_score: float) -> float:
    return _clamp(overall_score / 100.0)


def _reason(recommendation: str, overall_score: float, status: str) -> str:
    if status == "rejected":
        return (
            "Candidate was rejected during screening due to unmet minimum "
            "requirements (experience or must-have skills)."
        )

    if recommendation == "hire_high":
        return (
            "Strong technical and skill match with sufficient experience and "
            "interview performance. Candidate meets or exceeds all key criteria."
        )

    if recommendation == "hire_moderate":
        return (
            "Moderate alignment across criteria. Candidate clears the minimum "
            "bar but has some gaps worth exploring before a final decision."
        )

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
        Must contain ``status`` and ``evaluation.overall_score``.

    Returns
    -------
    dict with keys:
        recommendation – "hire_high" | "hire_moderate" | "no_hire"
        confidence     – float in [0, 1]
        reason         – str
    """
    status: str = candidate.get("status") or ""

    evaluation = candidate.get("evaluation") or {}
    try:
        overall_score = float(evaluation.get("overall_score") or 0.0)
    except (TypeError, ValueError):
        overall_score = 0.0

    overall_score = _clamp(overall_score, 0.0, 100.0)

    if status == "rejected":
        recommendation = "no_hire"
    elif overall_score >= _HIRE_HIGH_THRESHOLD:
        recommendation = "hire_high"
    elif overall_score >= _HIRE_MEDIUM_THRESHOLD:
        recommendation = "hire_moderate"
    else:
        recommendation = "no_hire"

    return {
        "recommendation": recommendation,
        "confidence":     round(_confidence(overall_score), 4),
        "reason":         _reason(recommendation, overall_score, status),
    }
