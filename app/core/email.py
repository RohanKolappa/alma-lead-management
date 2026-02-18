from __future__ import annotations

"""Email abstraction.

EmailBackend defines the interface for sending transactional emails.
ConsoleEmailBackend logs to the console for local development — swap in an
SMTP or SendGrid implementation by providing any class that satisfies the
Protocol.
"""

import logging
from typing import Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class EmailBackend(Protocol):
    """Protocol for email sending implementations."""

    async def send(self, to: str, subject: str, body: str) -> None:
        """Send an email to a single recipient."""
        ...


class ConsoleEmailBackend:
    """Logs emails to the console instead of sending them."""

    async def send(self, to: str, subject: str, body: str) -> None:
        preview = body[:200] + ("..." if len(body) > 200 else "")
        logger.info(
            "\n--- EMAIL ---\n"
            "To:      %s\n"
            "Subject: %s\n"
            "Body:\n%s\n"
            "--- END EMAIL ---",
            to,
            subject,
            preview,
        )


# ---------------------------------------------------------------------------
# Email templates
# ---------------------------------------------------------------------------

def prospect_confirmation_email(first_name: str) -> tuple[str, str]:
    """Return (subject, body) confirming we received a prospect's submission."""
    subject = "We've received your information"
    body = (
        f"Hi {first_name},\n\n"
        "Thank you for submitting your information. "
        "Our team will review your case and reach out to you shortly.\n\n"
        "Best regards,\n"
        "The Alma Team"
    )
    return subject, body


def attorney_notification_email(
    lead_first_name: str,
    lead_last_name: str,
    lead_email: str,
) -> tuple[str, str]:
    """Return (subject, body) notifying an attorney of a new lead."""
    subject = f"New lead: {lead_first_name} {lead_last_name}"
    body = (
        "A new lead has been submitted.\n\n"
        f"Name:  {lead_first_name} {lead_last_name}\n"
        f"Email: {lead_email}\n\n"
        "Please review and follow up."
    )
    return subject, body
