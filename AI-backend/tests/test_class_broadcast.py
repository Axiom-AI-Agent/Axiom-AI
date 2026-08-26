"""Class Telegram broadcast — audience resolution and dashboard HTTP API."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.messaging.class_broadcast import (
    BroadcastAudience,
    BroadcastFailure,
    BroadcastRecipient,
    BroadcastResult,
    ClassNotFoundError,
    format_announcement,
    resolve_broadcast_audience,
    send_class_broadcast,
)


def _chain_mock(data=None):
    mock = MagicMock()
    mock.execute.return_value = MagicMock(data=data or [])
    mock.select.return_value = mock
    mock.eq.return_value = mock
    mock.in_.return_value = mock
    return mock


def _supabase_tables(tables: dict[str, list[dict]]) -> MagicMock:
    client = MagicMock()

    def table_side_effect(name: str):
        return _chain_mock(data=tables.get(name, []))

    client.table.side_effect = table_side_effect
    return client


def _class_row() -> dict[str, str]:
    return {
        "id": "class-physics-al-2026",
        "name": "A/L Physics 2026",
        "subject": "Physics",
    }


@patch("services.messaging.class_broadcast.AdmissionsDbClient")
@patch("services.messaging.class_broadcast.get_supabase_client")
def test_audience_splits_reachable_and_skipped(mock_supa, mock_db_cls):
    mock_db_cls.return_value.get_class.return_value = _class_row()
    mock_supa.return_value = _supabase_tables(
        {
            "enrollments": [
                {"student_id": "s1", "status": "active"},
                {"student_id": "s2", "status": "pending"},
                {"student_id": "s3", "status": "active"},
                {"student_id": "s4", "status": "withdrawn"},
            ],
            "student_channels": [
                {"student_id": "s1", "channel_address": "111"},
                {"student_id": "s2", "channel_address": "not-a-number"},
            ],
            "students": [
                {"id": "s1", "name": "Amaya Perera", "phone": "94771234567"},
                {"id": "s2", "name": "Kasun", "phone": "94770000002"},
                {"id": "s3", "name": "Nimal", "phone": "94770000003"},
                {"id": "s4", "name": "Withdrawn", "phone": "94770000004"},
            ],
        }
    )

    audience = resolve_broadcast_audience(
        tenant_id="tenant-demo-physics",
        class_id="class-physics-al-2026",
    )

    assert audience.enrolled == 3
    assert audience.skipped_no_telegram == 2
    assert audience.reachable_names == ["Amaya"]
    assert len(audience.reachable) == 1
    assert audience.reachable[0].chat_id == 111
    assert audience.reachable[0].student_id == "s1"


@patch("services.messaging.class_broadcast.AdmissionsDbClient")
def test_audience_raises_when_class_missing(mock_db_cls):
    mock_db_cls.return_value.get_class.return_value = None
    with pytest.raises(ClassNotFoundError):
        resolve_broadcast_audience(tenant_id="tenant-demo-physics", class_id="missing")


@patch("services.messaging.class_broadcast.AdmissionsDbClient")
@patch("services.messaging.class_broadcast.get_supabase_client")
def test_empty_class_is_zero_reachable(mock_supa, mock_db_cls):
    mock_db_cls.return_value.get_class.return_value = _class_row()
    mock_supa.return_value = _supabase_tables(
        {"enrollments": [], "student_channels": [], "students": []}
    )

    audience = resolve_broadcast_audience(
        tenant_id="tenant-demo-physics",
        class_id="class-physics-al-2026",
    )

    assert audience.enrolled == 0
    assert audience.reachable == ()
    assert audience.skipped_no_telegram == 0


def test_format_announcement_prefixes_class_name():
    text = format_announcement("A/L Physics 2026", "  Exam is postponed.  ")
    assert text == "Class announcement — A/L Physics 2026\n\nExam is postponed."


@pytest.mark.asyncio
@patch("services.messaging.class_broadcast.MessagePersistence")
@patch("services.messaging.class_broadcast.send_telegram_message", new_callable=AsyncMock)
@patch("services.messaging.class_broadcast.resolve_broadcast_audience")
async def test_send_partial_failures(mock_audience, mock_send, mock_persistence_cls):
    mock_audience.return_value = BroadcastAudience(
        class_id="class-physics-al-2026",
        class_name="A/L Physics 2026",
        enrolled=2,
        reachable=(
            BroadcastRecipient("s1", "Amaya Perera", "94771234567", 111),
            BroadcastRecipient("s2", "Kasun", "94770000002", 222),
        ),
        skipped_no_telegram=1,
    )
    mock_send.side_effect = [{"ok": True}, RuntimeError("bot blocked")]
    persistence = MagicMock()
    mock_persistence_cls.return_value = persistence

    result = await send_class_broadcast(
        tenant_id="tenant-demo-physics",
        class_id="class-physics-al-2026",
        message="Exam postponed",
    )

    assert result.sent == 1
    assert result.failed == 1
    assert result.skipped_no_telegram == 1
    assert result.failures == (BroadcastFailure(student_id="s2", name="Kasun"),)
    assert mock_send.await_count == 2
    persistence.log_staff_reply.assert_called_once()
    logged_text = persistence.log_staff_reply.call_args.kwargs["body"]
    assert logged_text.startswith("Class announcement — A/L Physics 2026")


@pytest.mark.asyncio
@patch("services.messaging.class_broadcast.send_telegram_message", new_callable=AsyncMock)
@patch("services.messaging.class_broadcast.resolve_broadcast_audience")
async def test_send_empty_audience_does_not_call_telegram(mock_audience, mock_send):
    mock_audience.return_value = BroadcastAudience(
        class_id="class-physics-al-2026",
        class_name="A/L Physics 2026",
        enrolled=2,
        reachable=(),
        skipped_no_telegram=2,
    )

    result = await send_class_broadcast(
        tenant_id="tenant-demo-physics",
        class_id="class-physics-al-2026",
        message="Hello",
    )

    assert result == BroadcastResult(sent=0, failed=0, skipped_no_telegram=2, failures=())
    mock_send.assert_not_awaited()


@patch("api.routers.dashboard.broadcast.resolve_broadcast_audience")
def test_get_recipients_endpoint(mock_audience, client):
    mock_audience.return_value = BroadcastAudience(
        class_id="class-physics-al-2026",
        class_name="A/L Physics 2026",
        enrolled=3,
        reachable=(BroadcastRecipient("s1", "Amaya Perera", "94771234567", 111),),
        skipped_no_telegram=2,
    )

    response = client.get(
        "/dashboard/classes/class-physics-al-2026/broadcast-recipients",
        params={"tenant_id": "tenant-demo-physics"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reachable"] == 1
    assert body["skipped_no_telegram"] == 2
    assert body["reachable_names"] == ["Amaya"]
    assert "chat_id" not in body
    assert "111" not in str(body)


@patch("api.routers.dashboard.broadcast.resolve_broadcast_audience")
def test_get_recipients_404_when_class_missing(mock_audience, client):
    mock_audience.side_effect = ClassNotFoundError("missing")
    response = client.get(
        "/dashboard/classes/missing/broadcast-recipients",
        params={"tenant_id": "tenant-demo-physics"},
    )
    assert response.status_code == 404


def test_post_broadcast_rejects_empty_message(client):
    response = client.post(
        "/dashboard/classes/class-physics-al-2026/broadcast",
        json={"tenant_id": "tenant-demo-physics", "message": "   "},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


@patch("api.routers.dashboard.broadcast.send_class_broadcast", new_callable=AsyncMock)
def test_post_broadcast_returns_partial_counts(mock_send, client):
    mock_send.return_value = BroadcastResult(
        sent=1,
        failed=1,
        skipped_no_telegram=1,
        failures=(BroadcastFailure(student_id="s2", name="Kasun"),),
    )

    response = client.post(
        "/dashboard/classes/class-physics-al-2026/broadcast",
        json={"tenant_id": "tenant-demo-physics", "message": "Exam postponed"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["sent"] == 1
    assert body["failed"] == 1
    assert body["skipped_no_telegram"] == 1
    assert body["failures"] == [{"student_id": "s2", "name": "Kasun"}]
    mock_send.assert_awaited_once()


@patch("api.routers.dashboard.broadcast.send_class_broadcast", new_callable=AsyncMock)
def test_post_broadcast_404_when_class_missing(mock_send, client):
    mock_send.side_effect = ClassNotFoundError("missing")
    response = client.post(
        "/dashboard/classes/missing/broadcast",
        json={"tenant_id": "tenant-demo-physics", "message": "Hello"},
    )
    assert response.status_code == 404
