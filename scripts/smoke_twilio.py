#!/usr/bin/env python3
"""Smoke-test the Phase 1 WhatsApp pipeline without a live Twilio send."""

from __future__ import annotations

from unittest.mock import MagicMock

from dotenv import load_dotenv

load_dotenv(override=True)

from services.identity.context import IdentityContext
from services.messaging.pipeline import ChatPipeline
from services.messaging.schemas import TwilioInboundMessage
from services.messaging.twilio_client import TwilioMessagingClient


def main() -> None:
    inbound = TwilioInboundMessage.model_validate(
        {
            "MessageSid": "SM_SMOKE",
            "AccountSid": "AC_SMOKE",
            "From": "whatsapp:+94771234567",
            "To": "whatsapp:+14155238886",
            "Body": "Smoke test message",
            "NumMedia": 0,
        }
    )

    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-physics-001",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
    )

    resolver = MagicMock()
    resolver.resolve.return_value = ctx
    persistence = MagicMock()
    messaging = TwilioMessagingClient(dry_run=True)

    pipeline = ChatPipeline(resolver=resolver, messaging=messaging, persistence=persistence)
    result = pipeline.process_twilio(inbound)

    print("=== Phase 1 smoke-twilio ===")
    print("Reply:", result.reply)
    print("Dry-run send: OK")
    print("Persistence calls:", persistence.log_inbound.called, persistence.log_outbound.called)
    print("PASS")


if __name__ == "__main__":
    main()
