"""Twilio webhook endpoint tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from services.identity.context import IdentityContext
from services.messaging.schemas import TwilioInboundMessage, TwilioSendResult

WEBHOOK_URL = "https://testserver/webhooks/twilio"

FORM = {
    "MessageSid": "SM123",
    "AccountSid": "AC123",
    "From": "whatsapp:+94771234567",
    "To": "whatsapp:+14155238886",
    "Body": "Hello from sandbox",
    "NumMedia": "0",
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def identity_ctx():
    return IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-physics-001",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
        student_exists=True,
    )


def test_twilio_webhook_returns_200_immediately(client):
    with patch("api.webhooks.twilio._should_validate_signature", return_value=False):
        with patch("services.messaging.pipeline.ChatPipeline.aprocess_twilio", new_callable=AsyncMock) as mock_process:
            response = client.post("/webhooks/twilio", data=FORM)
            assert response.status_code == 200
            assert mock_process.called


def test_twilio_webhook_rejects_invalid_signature(client):
    with patch("api.webhooks.twilio._should_validate_signature", return_value=True):
        with patch("api.webhooks.twilio.validate_twilio_signature", return_value=False):
            response = client.post("/webhooks/twilio", data=FORM)
            assert response.status_code == 403


def test_twilio_webhook_requires_from_and_to(client):
    with patch("api.webhooks.twilio._should_validate_signature", return_value=False):
        response = client.post("/webhooks/twilio", data={"Body": "hi"})
        assert response.status_code == 400


def test_whatsapp_pipeline_logs_and_replies_dry_run(identity_ctx):
    inbound = TwilioInboundMessage.model_validate(
        {
            "MessageSid": "SM999",
            "AccountSid": "AC999",
            "From": "whatsapp:+94771234567",
            "To": "whatsapp:+14155238886",
            "Body": "Need help with physics",
            "NumMedia": 0,
        }
    )

    mock_resolver = MagicMock()
    mock_resolver.resolve.return_value = identity_ctx

    mock_persistence = MagicMock()
    mock_messaging = MagicMock()
    mock_messaging.send_whatsapp.return_value = TwilioSendResult(
        sid=None,
        status="dry_run",
        dry_run=True,
        detail="dry run",
    )

    from services.messaging.pipeline import ChatPipeline

    pipeline = ChatPipeline(
        resolver=mock_resolver,
        messaging=mock_messaging,
        persistence=mock_persistence,
    )
    result = pipeline.process_twilio(inbound)

    assert "Demo Physics Academy" in result.reply
    mock_persistence.log_inbound.assert_called_once()
    mock_persistence.log_outbound.assert_called_once()
    mock_messaging.send_whatsapp.assert_called_once()


def test_parse_twilio_form_extracts_media():
    from services.messaging.parser import parse_twilio_form

    parsed = parse_twilio_form(
        {
            **FORM,
            "NumMedia": "1",
            "MediaUrl0": "https://api.twilio.com/media/abc",
        }
    )
    assert parsed.num_media == 1
    assert parsed.media_url == "https://api.twilio.com/media/abc"
