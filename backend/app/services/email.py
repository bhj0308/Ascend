"""Email sending for password reset / email verification links.

Synchronous by design — no Celery task queue. Each send is a single fast
HTTP call (or a log line in dev), so it runs inline on the request that
triggers it rather than adding background-job infrastructure for it.
"""

import logging
from dataclasses import dataclass

from app.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    to: str
    subject: str
    text: str


class ConsoleEmailSender:
    """Dev/placeholder sender: logs the email instead of sending it."""

    def send(self, message: EmailMessage) -> None:
        logger.info(
            "\n===== EMAIL to %s =====\nSubject: %s\n\n%s\n===== END EMAIL =====",
            message.to,
            message.subject,
            message.text,
        )


class SendGridEmailSender:
    """Sends via the SendGrid API. Never raises — failures are logged only."""

    def send(self, message: EmailMessage) -> None:
        settings = get_settings()
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            mail = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=message.to,
                subject=message.subject,
                plain_text_content=message.text,
            )
            SendGridAPIClient(settings.SENDGRID_API_KEY).send(mail)
        except Exception:
            logger.exception("Failed to send email to %s via SendGrid", message.to)


class RecordingEmailSender:
    """Test sender: records messages instead of sending them."""

    def __init__(self) -> None:
        self.sent: list[EmailMessage] = []

    def send(self, message: EmailMessage) -> None:
        self.sent.append(message)


def get_email_sender():
    """Return the SendGrid sender if configured, else the console sender.

    Tests monkeypatch this by name on the importing module
    (`monkeypatch.setattr("app.routes.auth.get_email_sender", ...)`), since
    routes call `get_email_sender()` fresh on every request rather than
    caching a sender at import time.
    """
    settings = get_settings()
    if settings.SENDGRID_API_KEY:
        return SendGridEmailSender()
    return ConsoleEmailSender()
