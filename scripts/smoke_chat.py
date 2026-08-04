#!/usr/bin/env python3
"""Smoke-test the HTTP dev chat endpoint (no Twilio required)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from domain.enums import ChatChannel
from services.identity.context import IdentityContext
from services.messaging.pipeline import ChatPipeline
from services.messaging.schemas import InboundMessage


def main() -> None:
    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-physics-001",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
    )

    resolver = MagicMock()
    resolver.resolve_direct.return_value = ctx
    persistence = MagicMock()

    with patch.object(ChatPipeline, "_run_agent_turn", new_callable=AsyncMock) as mock_turn:
        mock_turn.return_value = "Hi! Welcome to Demo Physics Academy. How can I help you today?"
        pipeline = ChatPipeline(resolver=resolver, persistence=persistence)
        result = pipeline.process_message(
            InboundMessage(
                channel=ChatChannel.TWILIO_WHATSAPP,
                tenant_id="tenant-demo-physics",
                phone="94771234567",
                body="Hello, I want to join A/L Physics",
            )
        )

    print("=== Phase 2 smoke-chat ===")
    print("Reply:", result.reply)
    print("Session:", result.session_id)
    print("Persistence calls:", persistence.log_inbound.called, persistence.log_outbound.called)
    print("PASS")


if __name__ == "__main__":
    main()
