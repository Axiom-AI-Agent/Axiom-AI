"""Telegram webhook + ChatPipeline wiring tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from domain.enums import ChatChannel
from services.admissions.onboarding_session_store import get_onboarding_session_store
from services.messaging.schemas import ChatTurnResult, InboundMessage
from services.messaging.telegram_handlers import (
    handle_contact_shared,
    handle_photo_message,
    handle_text_message,
    handle_voice_message,
)
from services.tenant_config import TenantBotTokenError

STUDENT = {
    "id": "stu-physics-001",
    "tenant_id": "tenant-demo-physics",
    "name": "Amaya Perera",
    "phone": "94771234567",
}

PIPELINE_RESULT = ChatTurnResult(
    reply="Hello from Axiom",
    tenant_id="tenant-demo-physics",
    tenant_slug="demo-physics",
    tenant_name="Demo Physics Academy",
    student_id="stu-physics-001",
    phone="94771234567",
    session_id="tenant-demo-physics:94771234567",
    student_exists=True,
    channel=ChatChannel.TELEGRAM,
)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_telegram_webhook_text_for_known_student(client):
    with patch("api.webhooks.telegram.ensure_tenant_bot", new_callable=AsyncMock), patch(
        "api.webhooks.telegram.handle_text_message",
        new_callable=AsyncMock,
    ) as mock_text:
        response = client.post(
            "/webhooks/telegram/tenant-demo-physics",
            json={
                "update_id": 10,
                "message": {
                    "message_id": 1,
                    "chat": {"id": 555001},
                    "from": {"id": 77, "first_name": "Amaya"},
                    "text": "I want to join physics",
                },
            },
        )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    mock_text.assert_awaited_once()
    args = mock_text.await_args
    assert args.args[0] == "tenant-demo-physics"
    assert args.args[1] == 555001
    assert args.args[2] == "I want to join physics"


def test_telegram_webhook_unknown_tenant_still_acks(client):
    with patch(
        "api.webhooks.telegram.ensure_tenant_bot",
        new_callable=AsyncMock,
        side_effect=TenantBotTokenError("Unknown tenant: missing"),
    ), patch("api.webhooks.telegram.handle_text_message", new_callable=AsyncMock) as mock_text:
        response = client.post(
            "/webhooks/telegram/missing",
            json={"update_id": 1, "message": {"chat": {"id": 1}, "text": "hi"}},
        )
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    mock_text.assert_not_called()


def test_telegram_webhook_photo_and_voice_dispatch(client):
    with (
        patch("api.webhooks.telegram.ensure_tenant_bot", new_callable=AsyncMock),
        patch("api.webhooks.telegram.handle_photo_message", new_callable=AsyncMock) as mock_photo,
    ):
        response = client.post(
            "/webhooks/telegram/tenant-demo-physics",
            json={
                "update_id": 11,
                "message": {
                    "chat": {"id": 555001},
                    "photo": [{"file_id": "small"}, {"file_id": "large"}],
                    "caption": "slip",
                },
            },
        )
    assert response.status_code == 200
    mock_photo.assert_awaited_once()

    with (
        patch("api.webhooks.telegram.ensure_tenant_bot", new_callable=AsyncMock),
        patch("api.webhooks.telegram.handle_voice_message", new_callable=AsyncMock) as mock_voice,
    ):
        response = client.post(
            "/webhooks/telegram/tenant-demo-physics",
            json={
                "update_id": 12,
                "message": {"chat": {"id": 555001}, "voice": {"file_id": "ogg-1"}},
            },
        )
    assert response.status_code == 200
    mock_voice.assert_awaited_once()


def test_root_lists_telegram_webhook(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "/webhooks/telegram/{tenant_id}" in response.json()["telegram_webhook"]


@pytest.mark.asyncio
async def test_handle_text_calls_shared_pipeline_with_telegram_channel():
    with patch(
        "services.messaging.telegram_handlers.resolve_student",
        new_callable=AsyncMock,
        return_value=STUDENT,
    ), patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
        return_value=PIPELINE_RESULT,
    ) as mock_pipeline, patch(
        "services.messaging.telegram_handlers.send_telegram_message",
        new_callable=AsyncMock,
    ) as mock_send, patch(
        "services.messaging.telegram_handlers.bind_telegram_student_channel",
        new_callable=AsyncMock,
    ):
        await handle_text_message(
            "tenant-demo-physics",
            555001,
            "What time is class?",
            update_id=99,
        )

    inbound = mock_pipeline.await_args.args[-1]
    assert isinstance(inbound, InboundMessage)
    assert inbound.channel is ChatChannel.TELEGRAM
    assert inbound.tenant_id == "tenant-demo-physics"
    assert inbound.phone == "94771234567"
    assert inbound.body == "What time is class?"
    mock_send.assert_awaited_once_with("tenant-demo-physics", 555001, "Hello from Axiom")


@pytest.mark.asyncio
async def test_handle_text_new_user_requests_contact():
    with patch(
        "services.messaging.telegram_handlers.resolve_student",
        new_callable=AsyncMock,
        return_value=None,
    ), patch(
        "services.messaging.telegram_handlers.send_telegram_contact_request",
        new_callable=AsyncMock,
    ) as mock_contact, patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
    ) as mock_pipeline:
        await handle_text_message("tenant-demo-physics", 555001, "/start")

    mock_contact.assert_awaited_once()
    mock_pipeline.assert_not_called()


@pytest.mark.asyncio
async def test_handle_text_pending_phone_runs_pipeline():
    pending = {
        "id": None,
        "tenant_id": "tenant-demo-physics",
        "name": None,
        "phone": "94771234567",
    }
    with patch(
        "services.messaging.telegram_handlers.resolve_student",
        new_callable=AsyncMock,
        return_value=pending,
    ), patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
        return_value=PIPELINE_RESULT,
    ) as mock_pipeline, patch(
        "services.messaging.telegram_handlers.send_telegram_message",
        new_callable=AsyncMock,
    ), patch(
        "services.messaging.telegram_handlers.bind_telegram_student_channel",
        new_callable=AsyncMock,
    ):
        await handle_text_message("tenant-demo-physics", 555001, "hi")

    inbound = mock_pipeline.await_args.args[-1]
    assert inbound.phone == "94771234567"
    assert inbound.body == "hi"


@pytest.mark.asyncio
async def test_handle_text_passes_enrollment_phrasing_unchanged():
    pending = {
        "id": None,
        "tenant_id": "tenant-demo-physics",
        "name": None,
        "phone": "94771234567",
    }
    with patch(
        "services.messaging.telegram_handlers.resolve_student",
        new_callable=AsyncMock,
        return_value=pending,
    ), patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
        return_value=PIPELINE_RESULT,
    ) as mock_pipeline, patch(
        "services.messaging.telegram_handlers.send_telegram_message",
        new_callable=AsyncMock,
    ), patch(
        "services.messaging.telegram_handlers.bind_telegram_student_channel",
        new_callable=AsyncMock,
    ):
        await handle_text_message(
            "tenant-demo-physics",
            555001,
            "can I sign up for A/L physics this year?",
        )

    inbound = mock_pipeline.await_args.args[-1]
    assert inbound.body == "can I sign up for A/L physics this year?"


@pytest.mark.asyncio
async def test_handle_contact_starts_enrollment_for_new_phone():
    pending = {
        "id": None,
        "tenant_id": "tenant-demo-physics",
        "name": None,
        "phone": "94771234567",
    }
    with patch(
        "services.messaging.telegram_handlers.link_telegram_contact",
        new_callable=AsyncMock,
        return_value=pending,
    ) as mock_link, patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
        return_value=PIPELINE_RESULT,
    ) as mock_pipeline, patch(
        "services.messaging.telegram_handlers.send_telegram_message",
        new_callable=AsyncMock,
    ), patch(
        "services.messaging.telegram_handlers.bind_telegram_student_channel",
        new_callable=AsyncMock,
    ):
        await handle_contact_shared(
            "tenant-demo-physics",
            555001,
            {"phone_number": "+94771234567", "user_id": 77, "first_name": "Amaya"},
            {"id": 77, "first_name": "Amaya"},
        )

    mock_link.assert_awaited_once()
    inbound = mock_pipeline.await_args.args[-1]
    assert inbound.channel is ChatChannel.TELEGRAM
    assert inbound.phone == "94771234567"
    assert inbound.body == ""
    session = get_onboarding_session_store().get(
        tenant_id="tenant-demo-physics", phone="94771234567"
    )
    assert session is not None and session.active
    get_onboarding_session_store().clear(
        tenant_id="tenant-demo-physics", phone="94771234567"
    )


@pytest.mark.asyncio
async def test_handle_contact_greets_already_enrolled_student():
    with patch(
        "services.messaging.telegram_handlers.link_telegram_contact",
        new_callable=AsyncMock,
        return_value=STUDENT,
    ) as mock_link, patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
        return_value=PIPELINE_RESULT,
    ) as mock_pipeline, patch(
        "services.messaging.telegram_handlers.send_telegram_message",
        new_callable=AsyncMock,
    ), patch(
        "services.messaging.telegram_handlers.bind_telegram_student_channel",
        new_callable=AsyncMock,
    ):
        await handle_contact_shared(
            "tenant-demo-physics",
            555001,
            {"phone_number": "+94771234567", "user_id": 77, "first_name": "Amaya"},
            {"id": 77, "first_name": "Amaya"},
        )

    mock_link.assert_awaited_once()
    inbound = mock_pipeline.await_args.args[-1]
    assert inbound.body == "Hello"


@pytest.mark.asyncio
async def test_handle_photo_passes_media_url_into_pipeline():
    with patch(
        "services.messaging.telegram_handlers.resolve_student",
        new_callable=AsyncMock,
        return_value=STUDENT,
    ), patch(
        "services.messaging.telegram_handlers.resolve_telegram_file_url",
        new_callable=AsyncMock,
        return_value="https://api.telegram.org/file/bot111:AAA/photos/slip.jpg",
    ), patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
        return_value=PIPELINE_RESULT,
    ) as mock_pipeline, patch(
        "services.messaging.telegram_handlers.send_telegram_message",
        new_callable=AsyncMock,
    ), patch(
        "services.messaging.telegram_handlers.bind_telegram_student_channel",
        new_callable=AsyncMock,
    ):
        await handle_photo_message(
            "tenant-demo-physics",
            555001,
            [{"file_id": "small"}, {"file_id": "large"}],
            caption="bank slip",
        )

    inbound = mock_pipeline.await_args.args[-1]
    assert inbound.media_url.endswith("photos/slip.jpg")
    assert inbound.num_media == 1
    assert inbound.body == "bank slip"
    assert inbound.channel is ChatChannel.TELEGRAM


@pytest.mark.asyncio
async def test_handle_voice_does_not_call_pipeline():
    with patch(
        "services.messaging.telegram_handlers.send_telegram_message",
        new_callable=AsyncMock,
    ) as mock_send, patch(
        "services.messaging.telegram_handlers.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
    ) as mock_pipeline:
        await handle_voice_message("tenant-demo-physics", 555001, {"file_id": "ogg-1"})

    mock_pipeline.assert_not_called()
    mock_send.assert_awaited_once()
    assert "Voice notes" in mock_send.await_args.args[2]


@pytest.mark.asyncio
async def test_register_webhook_url_includes_tenant_path():
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parents[1] / "scripts" / "register_telegram_webhook.py"
    spec = importlib.util.spec_from_file_location("register_telegram_webhook", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    set_resp = MagicMock()
    set_resp.json.return_value = {"ok": True, "result": True}
    info_resp = MagicMock()
    info_resp.json.return_value = {
        "ok": True,
        "result": {"url": "https://example.com/webhooks/telegram/tenant-demo-physics"},
    }

    client = AsyncMock()
    client.get.side_effect = [set_resp, info_resp]
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=None)

    with patch.object(module, "httpx") as mock_httpx:
        mock_httpx.AsyncClient.return_value = cm
        result = await module.register_webhook(
            "111:AAA",
            "tenant-demo-physics",
            "https://example.com",
        )

    set_call = client.get.await_args_list[0]
    assert set_call.kwargs["params"]["url"] == "https://example.com/webhooks/telegram/tenant-demo-physics"
    assert result["setWebhook"]["ok"] is True
