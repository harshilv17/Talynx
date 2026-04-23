"""Feature 4 – Offer generation and email delivery."""
import datetime
import logging

from feature3.email_sender import send_email

logger = logging.getLogger(__name__)


def _get_candidate_email(candidate: dict) -> str:
    """Resolve candidate email from outreach record or direct field."""
    return (
        candidate.get("email")
        or (candidate.get("outreach") or {}).get("email_address")
        or ""
    )


def _compute_salary(overall_score: float, jd: dict) -> str:
    """
    Derive salary offer from JD salary band, scaled by candidate score.

    Looks for min_salary / max_salary (or salary_min / salary_max) in the JD.
    Falls back to sensible defaults if band is absent.
    All values are in INR (annual).
    """
    try:
        min_sal = float(jd.get("min_salary") or jd.get("salary_min") or 800_000)
        max_sal = float(jd.get("max_salary") or jd.get("salary_max") or 2_500_000)
    except (TypeError, ValueError):
        min_sal, max_sal = 800_000.0, 2_500_000.0

    if max_sal <= min_sal:
        max_sal = min_sal * 1.5

    score_fraction = max(0.0, min(1.0, overall_score / 100.0))
    computed = int(min_sal + score_fraction * (max_sal - min_sal))

    lpa = computed / 100_000
    return f"₹{lpa:.2f} LPA"


def generate_offer(candidate: dict, jd: dict) -> str:
    """
    Generate a structured, personalised offer letter.

    Salary is derived dynamically from the JD salary band and candidate score.
    """
    name         = candidate.get("name", "Candidate")
    role         = jd.get("job_title") or jd.get("role") or "Software Engineer"
    company_name = jd.get("company_name") or jd.get("company") or "Talynx AI"

    evaluation    = candidate.get("evaluation") or {}
    overall_score = 0.0
    try:
        overall_score = float(evaluation.get("overall_score") or candidate.get("score") or 0.0)
    except (TypeError, ValueError):
        overall_score = 0.0

    compensation  = _compute_salary(overall_score, jd)
    joining_date  = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%d %B %Y")
    company_blurb = jd.get("company_blurb") or f"{company_name} is a fast-growing AI-powered talent platform."

    return f"""Dear {name},

Congratulations! We are thrilled to extend an offer for the position of {role} at {company_name}.

{company_blurb}

Offer Details:
  • Role              : {role}
  • Compensation      : {compensation} (annual, fixed)
  • Expected Joining  : {joining_date}
  • Work Mode         : Remote / HQ (as agreed)

We were impressed by your background and believe you will make a meaningful contribution to our team. Please reply to this email to confirm acceptance, or let us know if you have any questions.

We look forward to welcoming you aboard.

Best regards,
Talent Acquisition Team
{company_name}
"""


def send_offer_email(candidate: dict, offer_text: str) -> dict:
    """
    Send the generated offer letter to the candidate.

    Returns the provider result dict on success, raises Exception on failure.
    """
    email = _get_candidate_email(candidate)
    if not email:
        raise ValueError(
            f"No email address on record for candidate '{candidate.get('name')}'. "
            "Ensure outreach was completed before sending an offer."
        )

    name    = candidate.get("name", "Candidate")
    subject = f"Offer Letter – {name}"

    result = send_email(email, subject, offer_text)
    logger.info("Offer email sent to %s via %s", email, result.get("provider"))
    return result


def send_rejection_email(candidate: dict) -> dict:
    """
    Send a respectful rejection notification to the candidate.

    Returns the provider result dict on success, raises Exception on failure.
    """
    email = _get_candidate_email(candidate)
    if not email:
        raise ValueError(
            f"No email address on record for candidate '{candidate.get('name')}'. "
            "Ensure outreach was completed before sending a rejection."
        )

    name = candidate.get("name", "Candidate")
    body = f"""Dear {name},

Thank you for your interest and for the time you invested in our evaluation process.

After careful consideration, we have decided not to move forward with your application at this stage. This was a competitive process, and we appreciate the effort you put in.

We will keep your profile on file and encourage you to apply for future openings that match your background.

We wish you the very best in your career journey.

Warm regards,
Talent Acquisition Team
Talynx AI
"""
    subject = "Update on Your Application"
    result  = send_email(email, subject, body)
    logger.info("Rejection email sent to %s via %s", email, result.get("provider"))
    return result
