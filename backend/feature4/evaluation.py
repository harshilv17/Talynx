"""Feature 4 – Phase 1: Evaluation Scorecard (compute_final_score).

Produces a deterministic scorecard for a candidate against a job description.
Weights: technical 30%, experience 20%, skill_match 20%, interview 30%.
"""


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _technical_score(candidate: dict) -> float:
    raw = candidate.get("score") or candidate.get("match_score") or 0.0
    try:
        raw = float(raw)
    except (TypeError, ValueError):
        raw = 0.0
    return _clamp(raw)


def _experience_score(candidate: dict, jd: dict) -> float:
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
    must_haves = [s.lower().strip() for s in jd.get("must_have_skills", []) if s]
    if not must_haves:
        return 100.0

    cand_skills = [s.lower().strip() for s in candidate.get("skills", []) if s]
    if not cand_skills:
        return 0.0

    matched = sum(
        1
        for req in must_haves
        if any(req in cs or cs in req for cs in cand_skills)
    )
    return _clamp((matched / len(must_haves)) * 100.0)


def _interview_score(candidate: dict) -> float:
    raw = candidate.get("interview_score") or 0.0
    try:
        raw = float(raw)
    except (TypeError, ValueError):
        raw = 0.0
    return _clamp(raw)


def _build_summary(
    technical: float,
    experience: float,
    skill_match: float,
    interview: float,
    overall: float,
    candidate: dict,
    jd: dict,
) -> str:
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
        f"Technical fit score: {technical:.1f}/100.",
        f"Experience score: {experience:.1f}/100 "
        f"({candidate_exp} yr(s) vs {required_exp} yr(s) required).",
        f"Skill match score: {skill_match:.1f}/100"
        + (f" — missing skills: {', '.join(missing)}." if missing else " — all must-have skills matched."),
        f"Interview score: {interview:.1f}/100"
        + (" — no interview data recorded." if interview == 0.0 and not candidate.get("interview_score") else "."),
        f"Overall score: {overall:.1f}/100.",
    ]

    if overall >= 75:
        lines.append("Recommendation: Strong candidate — recommend advancing to offer stage.")
    elif overall >= 50:
        lines.append("Recommendation: Moderate fit — recommend human review before decision.")
    else:
        lines.append("Recommendation: Below threshold — does not meet minimum requirements.")

    return " ".join(lines)


def compute_final_score(candidate: dict, jd: dict) -> dict:
    """
    Compute a structured evaluation scorecard for *candidate* against *jd*.

    Weights: technical 30%, experience 20%, skill_match 20%, interview 30%.

    Returns dict with: technical_score, experience_score, skill_match_score,
    interview_score, overall_score, summary.
    """
    technical   = _technical_score(candidate)
    experience  = _experience_score(candidate, jd)
    skill_match = _skill_match_score(candidate, jd)
    interview   = _interview_score(candidate)

    overall = _clamp(
        technical   * 0.30
        + experience  * 0.20
        + skill_match * 0.20
        + interview   * 0.30
    )

    summary = _build_summary(technical, experience, skill_match, interview, overall, candidate, jd)

    return {
        "technical_score":   round(technical,   2),
        "experience_score":  round(experience,  2),
        "skill_match_score": round(skill_match, 2),
        "interview_score":   round(interview,   2),
        "overall_score":     round(overall,     2),
        "summary":           summary,
    }


# Backwards-compatible alias
evaluate_candidate = compute_final_score
