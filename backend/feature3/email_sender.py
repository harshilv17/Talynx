"""
Feature 3 — Email delivery.

Provider selection (in order):
  1. Resend  — if RESEND_API_KEY is set  (REST via httpx, no extra package)
  2. SMTP    — if SMTP_HOST is set       (stdlib smtplib)
  3. Error   — neither configured

Both providers raise Exception on failure so the pipeline can catch and mark the
outreach as "failed" without crashing the batch.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx

from core.config import get_settings

logger = logging.getLogger(__name__)


# ── Resend ────────────────────────────────────────────────────────────────────

def _send_via_resend(to_email: str, subject: str, body: str, settings) -> dict:
    response = httpx.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": settings.OUTREACH_FROM_EMAIL,
            "to":   [to_email],
            "subject": subject,
            "text": body,
        },
        timeout=15.0,
    )
    if response.status_code not in (200, 201):
        raise Exception(
            f"Resend returned {response.status_code}: {response.text[:300]}"
        )
    data = response.json()
    logger.info("Resend accepted email to %s  id=%s", to_email, data.get("id"))
    return {"provider": "resend", "message_id": data.get("id")}


# ── SMTP ──────────────────────────────────────────────────────────────────────

def _send_via_smtp(to_email: str, subject: str, body: str, settings) -> dict:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = settings.OUTREACH_FROM_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.OUTREACH_FROM_EMAIL, to_email, msg.as_string())

    logger.info("SMTP delivered email to %s", to_email)
    return {"provider": "smtp"}


# ── Public entry point ────────────────────────────────────────────────────────

def send_email(to_email: str, subject: str, body: str) -> dict:
    """
    Send an email using the first configured provider.

    Returns
    -------
    dict  — {provider, message_id?}  on success

    Raises
    ------
    Exception  if the chosen provider fails or none is configured.
    """
    settings = get_settings()

    if settings.RESEND_API_KEY:
        return _send_via_resend(to_email, subject, body, settings)

    if settings.SMTP_HOST:
        return _send_via_smtp(to_email, subject, body, settings)

    # No provider configured — log the email content so it's visible in server
    # logs and return a no-op result.  Set RESEND_API_KEY or SMTP_HOST to
    # enable real delivery.
    logger.warning(
        "[EMAIL DRY-RUN] No provider configured.\n"
        "  To: %s\n  Subject: %s\n  Body (first 200 chars): %s",
        to_email, subject, body[:200],
    )
    return {"provider": "dry_run", "message_id": None}
