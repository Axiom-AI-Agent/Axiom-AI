"""Dashboard API HTTP tests (mocked Supabase + CRM)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _chain_mock(data=None, count=0):
    mock = MagicMock()
    mock.execute.return_value = MagicMock(data=data or [], count=count)
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.in_.return_value = mock
    mock.order.return_value = mock
    mock.limit.return_value = mock
    return mock


@patch("api.routers.dashboard.escalations.get_supabase_client")
@patch("api.routers.dashboard.escalations.CrmTool")
def test_resolve_payment_escalation(mock_crm_cls, mock_supa, client):
    supa = MagicMock()
    mock_supa.return_value = supa
    supa.table.return_value = _chain_mock(
        data=[{"id": "esc-1", "reason_code": "payment_receipt"}]
    )

    mock_crm = MagicMock()
    mock_crm_cls.return_value = mock_crm
    mock_crm.resolve_escalation.return_value = json.dumps(
        {
            "ok": True,
            "student": {"phone": "94771234567", "name": "Amaya"},
            "class": {"name": "A/L Physics"},
            "enrollment": {"status": "active"},
        }
    )

    with patch(
        "api.routers.dashboard.escalations.notify_student",
        return_value=True,
    ) as notify:
        response = client.patch(
            "/dashboard/escalations/esc-1/resolve",
            params={"tenant_id": "tenant-demo-physics", "notify": "true"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["resolution"] == "approved"
    assert body["student_notified"] is True
    notify.assert_called_once()


@patch("api.routers.dashboard.escalations.get_supabase_client")
@patch("api.routers.dashboard.escalations.CrmTool")
def test_reject_payment_escalation(mock_crm_cls, mock_supa, client):
    mock_supa.return_value = MagicMock(
        table=MagicMock(return_value=_chain_mock(data=[{"id": "tenant-demo-physics", "name": "Demo"}]))
    )
    mock_crm = MagicMock()
    mock_crm_cls.return_value = mock_crm
    mock_crm.reject_payment_escalation.return_value = json.dumps(
        {
            "ok": True,
            "reason_code": "payment_receipt",
            "student": {"phone": "94771234567", "name": "Amaya"},
        }
    )

    with patch(
        "api.routers.dashboard.escalations.notify_student",
        return_value=True,
    ):
        response = client.patch(
            "/dashboard/escalations/esc-1/reject",
            params={"tenant_id": "tenant-demo-physics"},
        )

    assert response.status_code == 200
    assert response.json()["resolution"] == "rejected"


@patch("api.routers.dashboard.overview.get_supabase_client")
def test_dashboard_overview(mock_supa, client):
    supa = MagicMock()
    mock_supa.return_value = supa
    supa.table.return_value = _chain_mock(count=2)
    response = client.get(
        "/dashboard/overview",
        params={"tenant_id": "tenant-demo-physics"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "tenant-demo-physics"
    assert "open_escalations" in body


@patch("api.routers.dashboard.chat_logs.MessagePersistence")
def test_dashboard_chat_logs(mock_persistence_cls, client):
    mock_persistence = MagicMock()
    mock_persistence_cls.return_value = mock_persistence
    mock_persistence.get_turns.return_value = [
        {
            "id": "turn-1",
            "role": "user",
            "content": "Hello",
            "created_at": "2026-08-04T12:00:00Z",
        }
    ]
    response = client.get(
        "/dashboard/chat-logs",
        params={"tenant_id": "tenant-demo-physics", "phone": "94771234567"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["turns"]) == 1


@patch("api.routers.dashboard.chat.notify_student", return_value=True)
def test_dashboard_staff_send(mock_notify, client):
    response = client.post(
        "/dashboard/chat/send",
        json={
            "tenant_id": "tenant-demo-physics",
            "phone": "94771234567",
            "message": "Staff reply here",
        },
    )
    assert response.status_code == 200
    assert response.json()["delivered"] is True
    mock_notify.assert_called_once()
