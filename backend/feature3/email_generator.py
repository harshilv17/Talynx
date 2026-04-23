"""
Feature 3 — LLM-based outreach email generation.

Uses Groq (llama-3.3-70b-versatile), the same model as Feature 1,
to produce a personalized subject + body for each candidate.
"""
import json
import logging

from core.openai_client import get_groq_client

logger = logging.getLogger(__name__)

_MODEL       = "llama-3.3-70b-versatile"
_MAX_RETRIES = 2


def _build_prompt(candidate: dict, jd: dict) -> str:
    name        = candidate.get("name", "the candidate")
    skills      = ", ".join(candidate.get("skills", [])[:6]) or "various technologies"
    experience  = candidate.get("experience", 0)
    resume_text = (candidate.get("resume_text") or "")[:500]

    job_title     = jd.get("job_title", "the role")
    company_blurb = jd.get("company_blurb", "our company")
    about_role    = jd.get("about_role", "")
    requirements  = "\n".join(f"- {r}" for r in jd.get("requirements", [])[:3])

    return f"""You are a senior technical recruiter writing a personalized outreach email to a software engineer.

CANDIDATE PROFILE:
- Name: {name}
- Years of experience: {experience}
- Key skills: {skills}
- Background summary: {resume_text}

JOB DETAILS:
- Role: {job_title}
- Company context: {company_blurb}
- What the role involves: {about_role}
- Key requirements:
{requirements}

RULES FOR THE EMAIL:
1. Address the candidate by their first name only.
2. Mention 2-3 of their specific skills that directly match the role — be concrete.
3. Keep the total email under 180 words.
4. Use a warm, direct, human tone — no hollow openers like "I hope this email finds you well".
5. End with a clear call-to-action: ask them to reply if they are open to a quick call.
6. Do NOT mention salary or compensation.
7. Do NOT use markdown in the body — plain text only.

Return ONLY a valid JSON object, no markdown fences, no explanation:
{{
  "subject": "a compelling subject line under 60 characters",
  "body": "the full plain-text email body"
}}"""


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` wrapping that some LLMs add despite instructions."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # drop first and last fence lines
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return text.strip()


def generate_outreach_email(candidate: dict, jd: dict) -> dict:
    """
    Generate a personalized outreach email for a candidate.

    Returns
    -------
    dict with keys:
        subject : str
        body    : str

    Raises
    ------
    Exception  if generation fails after all retries.
    """
    client  = get_groq_client()
    prompt  = _build_prompt(candidate, jd)
    messages = [
        {"role": "system",  "content": prompt},
        {"role": "user",    "content": "Generate the outreach email now."},
    ]

    last_error: Exception | None = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=_MODEL,
                messages=messages,
            )
            raw     = response.choices[0].message.content
            cleaned = _strip_markdown_fences(raw)
            result  = json.loads(cleaned)

            subject = result.get("subject", "").strip()
            body    = result.get("body", "").strip()
            if not subject or not body:
                raise ValueError("LLM response missing 'subject' or 'body'")

            return {"subject": subject, "body": body}

        except Exception as exc:
            last_error = exc
            logger.warning("Email generation attempt %d/%d failed: %s", attempt + 1, _MAX_RETRIES + 1, exc)

    raise Exception(
        f"Email generation failed after {_MAX_RETRIES + 1} attempts: {last_error}"
    )
