"""Send WhatsApp messages via Twilio REST API."""

from __future__ import annotations

from loguru import logger

from infrastructure.config import (
    MESSAGING_DRY_RUN,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
)
from services.identity.resolver import normalize_whatsapp_address
from services.messaging.plaintext import strip_markdown_markers
from services.messaging.schemas import TwilioSendResult


class TwilioMessagingClient:
    """Thin wrapper around Twilio Messages API with dry-run support."""

    def __init__(
        self,
        *,
        account_sid: str | None = None,
        auth_token: str | None = None,
        from_number: str | None = None,
        dry_run: bool | None = None,
    ) -> None:
        self.account_sid = account_sid if account_sid is not None else TWILIO_ACCOUNT_SID
        self.auth_token = auth_token if auth_token is not None else TWILIO_AUTH_TOKEN
        self.from_number = from_number if from_number is not None else TWILIO_WHATSAPP_FROM
        self.dry_run = MESSAGING_DRY_RUN if dry_run is None else dry_run

    def send_whatsapp(
        self,
        *,
        to_number: str,
        body: str,
        media_url: str | None = None,
        from_number: str | None = None,
    ) -> TwilioSendResult:
        sender = from_number or self.from_number
        recipient = normalize_whatsapp_address(to_number)
        body = strip_markdown_markers(body)

        if self.dry_run:
            logger.info(
                "DRY-RUN WhatsApp to={} from={} body={!r} media={}",
                recipient,
                sender,
                body[:120],
                media_url,
            )
            return TwilioSendResult(
                sid=None,
                status="dry_run",
                dry_run=True,
                detail="MESSAGING_DRY_RUN=true — message not sent",
            )

        if not self.account_sid or not self.auth_token:
            logger.error("Twilio credentials missing — cannot send message")
            return TwilioSendResult(
                sid=None,
                status="error",
                detail="TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not configured",
            )

        from twilio.rest import Client

        client = Client(self.account_sid, self.auth_token)
        kwargs: dict[str, str] = {
            "from_": sender,
            "to": recipient,
            "body": body,
        }
        if media_url:
            kwargs["media_url"] = [media_url]

        message = client.messages.create(**kwargs)
        logger.info("Sent WhatsApp sid={} to={}", message.sid, recipient)
        return TwilioSendResult(
            sid=message.sid,
            status=str(message.status),
            dry_run=False,
            detail="sent",
        )
