"""HTTP dev chat endpoint tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from domain.enums import ChatChannel
from services.messaging.schemas import ChatTurnResult

CHAT_BODY = {
    "tenant_id": "tenant-demo-physics",
    "phone": "94771234567",
    "message": "What classes do you offer?",
}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def chat_result():
    return ChatTurnResult(
        reply="Thanks for messaging Demo Physics Academy! Axiom AI is connected.",
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-physics-001",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
        student_exists=True,
        channel=ChatChannel.HTTP_DEV,
    )


def test_chat_returns_reply(client, chat_result):
    with patch("api.routers.chat.ChatPipeline.aprocess_message", new_callable=AsyncMock, return_value=chat_result):
        response = client.post("/chat", json=CHAT_BODY)
    assert response.status_code == 200
    body = response.json()
    assert "Demo Physics Academy" in body["reply"]
    assert body["tenant_id"] == "tenant-demo-physics"
    assert body["session_id"] == "tenant-demo-physics:94771234567"


def test_chat_requires_message(client):
    response = client.post(
        "/chat",
        json={"tenant_id": "tenant-demo-physics", "phone": "94771234567", "message": ""},
    )
    assert response.status_code == 422


def test_chat_unknown_tenant_returns_404(client):
    with patch(
        "api.routers.chat.ChatPipeline.aprocess_message",
        new_callable=AsyncMock,
        side_effect=ValueError("Unknown tenant: missing"),
    ):
        response = client.post(
            "/chat",
            json={"tenant_id": "missing", "phone": "94771234567", "message": "Hi"},
        )
    assert response.status_code == 404


def test_get_chat_turns(client):
    mock_rows = [
        {
            "id": "turn-1",
            "role": "user",
            "content": "Hello",
            "created_at": "2026-08-04T12:00:00Z",
        },
        {
            "id": "turn-2",
            "role": "assistant",
            "content": "Hi there!",
            "created_at": "2026-08-04T12:00:01Z",
        },
    ]
    with patch("api.routers.chat.MessagePersistence.get_turns", return_value=mock_rows):
        response = client.get(
            "/chat/turns",
            params={"tenant_id": "tenant-demo-physics", "phone": "94771234567"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == "tenant-demo-physics:94771234567"
    assert len(body["turns"]) == 2
    assert body["turns"][0]["role"] == "user"


@pytest.mark.asyncio
async def test_chat_pipeline_runs_agent_inside_event_loop():
    """Regression: /chat must not call asyncio.run() inside FastAPI's event loop."""
    from services.identity.context import IdentityContext
    from services.messaging.pipeline import ChatPipeline
    from services.messaging.schemas import InboundMessage

    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-physics-001",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
        student_exists=True,
    )
    resolver = MagicMock()
    resolver.resolve_direct.return_value = ctx
    persistence = MagicMock()
    pipeline = ChatPipeline(resolver=resolver, persistence=persistence)

    with patch.object(
        pipeline,
        "_run_agent_turn",
        new_callable=AsyncMock,
        return_value="Hello from the agent",
    ):
        result = await pipeline.aprocess_message(
            InboundMessage(
                channel=ChatChannel.HTTP_DEV,
                tenant_id="tenant-demo-physics",
                phone="94771234567",
                body="Hi",
            )
        )

    assert result.reply == "Hello from the agent"
    persistence.log_inbound.assert_called_once()
    persistence.log_outbound.assert_called_once()
