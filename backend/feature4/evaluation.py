"""Feature 4 – Phase 1: Evaluation Scorecard.

Produces a structured, deterministic scorecard for a candidate against a
job description (role_brief).  No LLM is used; all scores are computed
from structured fields already present in the candidate and JD documents.
"""


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Clamp a value to [lo, hi]."""
    return max(lo, min(hi, value))


def _technical_score(candidate: dict) -> float:
    """
    Normalise the existing cosine-similarity match_score (0–100) to the
    same 0–100 range.  The field is already stored as a percentage by the
    ranking node, so we just clamp it for safety.
    """
    raw = candidate.get("score") or candidate.get("match_score") or 0.0
    try:
        raw = float(raw)
    except (TypeError, ValueError):
        raw = 0.0
    return _clamp(raw)


def _experience_score(candidate: dict, jd: dict) -> float:
    """
    Score how well the candidate's experience meets the JD requirement.

    * Meets or exceeds requirement → 100
    * Below requirement → linearly scaled (0 if 0 years, proportional otherwise)
    * No JD requirement → full marks (not penalised)
    """
    required = jd.get("years_of_experience") or 0
    try:
        required = float(required)
    except (TypeError, ValueError):
        required = 0.0

    if required <= 0:
        return 100.0

    candidate_exp = candidate.get("experience") or 0
    try:
        candidate_exp = float(candidate_exp)
    except (TypeError, ValueError):
        candidate_exp = 0.0

    if candidate_exp >= required:
        return 100.0

    return _clamp((candidate_exp / required) * 100.0)


def _skill_match_score(candidate: dict, jd: dict) -> float:
    """
    Percentage of JD must-have skills present in the candidate's skill set.
    Matching is case-insensitive and uses substring containment so that
    e.g. "React" matches "ReactJS".
    """
    must_haves = [s.lower().strip() for s in jd.get("must_have_skills", []) if s]
    if not must_haves:
        return 100.0  # No requirements → full marks

    cand_skills = [s.lower().strip() for s in candidate.get("skills", []) if s]
    if not cand_skills:
        return 0.0

    matched = sum(
        1
        for req in must_haves
        if any(req in cs or cs in req for cs in cand_skills)
    )
    return _clamp((matched / len(must_haves)) * 100.0)


def _build_summary(
    technical: float,
    experience: float,
    skill_match: float,
    overall: float,
    candidate: dict,
    jd: dict,
) -> str:
    """Return a human-readable, single-paragraph evaluation summary."""
    name = candidate.get("name", "The candidate")
    role = jd.get("job_title") or jd.get("role") or "the role"
    required_exp = jd.get("years_of_experience") or 0
    candidate_exp = candidate.get("experience") or 0

    must_haves = [s.lower().strip() for s in jd.get("must_have_skills", []) if s]
    cand_skills = [s.lower().strip() for s in candidate.get("skills", []) if s]
    missing = [
        req for req in must_haves
        if not any(req in cs or cs in req for cs in cand_skills)
    ]

    lines = [
        f"{name} was evaluated for {role}.",
        f"Technical fit score: {technical:.1f}/100 (based on JD similarity ranking).",
        f"Experience score: {experience:.1f}/100 "
        f"({candidate_exp} yr(s) vs {required_exp} yr(s) required).",
        f"Skill match score: {skill_match:.1f}/100"
        + (f" — missing skills: {', '.join(missing)}." if missing else " — all must-have skills matched."),
        f"Overall score: {overall:.1f}/100.",
    ]

    if overall >= 75:
        lines.append("Recommendation: Strong candidate — recommend advancing to the next stage.")
    elif overall >= 50:
        lines.append("Recommendation: Moderate fit — consider for further review.")
    else:
        lines.append("Recommendation: Below threshold — may not meet minimum requirements.")

    return " ".join(lines)


def evaluate_candidate(candidate: dict, jd: dict) -> dict:
    """
    Compute a structured evaluation scorecard for *candidate* against *jd*.

    Parameters
    ----------
    candidate : dict
        Candidate document from MongoDB (must contain at least ``score``,
        ``experience``, and ``skills``).
    jd : dict
        Role-brief / JD document (used for ``years_of_experience`` and
        ``must_have_skills``).

    Returns
    -------
    dict with keys:
        technical_score    – float 0-100
        experience_score   – float 0-100
        skill_match_score  – float 0-100
        overall_score      – float 0-100
        summary            – str
    """
    technical   = _technical_score(candidate)
    experience  = _experience_score(candidate, jd)
    skill_match = _skill_match_score(candidate, jd)

    # Weighted combination: 50% technical, 30% experience, 20% skills
    overall = _clamp(
        technical   * 0.50
        + experience  * 0.30
        + skill_match * 0.20
    )

    summary = _build_summary(technical, experience, skill_match, overall, candidate, jd)

    return {
        "technical_score":   round(technical,   2),
        "experience_score":  round(experience,  2),
        "skill_match_score": round(skill_match, 2),
        "overall_score":     round(overall,     2),
        "summary":           summary,
    }
