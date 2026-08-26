"""Student channel resolution tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from domain.enums import ChatChannel
from services.identity.student_resolver import (
    bind_telegram_student_channel,
    link_telegram_contact,
    resolve_student,
)
from services.identity.telegram_pending_store import get_telegram_pending_store

STUDENT = {
    "id": "stu-physics-001",
    "tenant_id": "tenant-demo-physics",
    "name": "Amaya Perera",
    "phone": "94771234567",
}


class _Query:
    def __init__(self, data):
        self._data = data
        self.inserted = None
        self.upserted = None
        self.deleted = False

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def insert(self, payload):
        self.inserted = payload
        self._data = [payload]
        return self

    def upsert(self, payload, on_conflict=None):
        self.upserted = payload
        self.on_conflict = on_conflict
        return self

    def delete(self):
        self.deleted = True
        return self

    def execute(self):
        result = MagicMock()
        result.data = self._data
        return result


def _client(tables: dict[str, _Query]) -> MagicMock:
    client = MagicMock()
    client.table.side_effect = lambda name: tables[name]
    return client


@pytest.fixture(autouse=True)
def clear_pending_store():
    store = get_telegram_pending_store()
    store.clear()
    yield
    store.clear()


@pytest.mark.asyncio
async def test_resolve_student_returns_linked_row():
    tables = {
        "student_channels": _Query([{"student_id": "stu-physics-001"}]),
        "students": _Query([STUDENT]),
        "enrollments": _Query([{"id": "enr-1", "status": "active"}]),
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await resolve_student(
            "tenant-demo-physics",
            ChatChannel.TELEGRAM.value,
            "555001",
        )
    assert student is not None
    assert student["id"] == "stu-physics-001"
    assert student["phone"] == "94771234567"


@pytest.mark.asyncio
async def test_resolve_student_returns_none_for_new_chat():
    tables = {
        "student_channels": _Query([]),
        "students": _Query([]),
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await resolve_student("tenant-demo-physics", "telegram", "999")
    assert student is None


@pytest.mark.asyncio
async def test_resolve_student_returns_pending_phone():
    get_telegram_pending_store().put(
        tenant_id="tenant-demo-physics",
        chat_id="555002",
        phone="94770001111",
    )
    tables = {
        "student_channels": _Query([]),
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await resolve_student("tenant-demo-physics", "telegram", "555002")
    assert student is not None
    assert student["id"] is None
    assert student["phone"] == "94770001111"


@pytest.mark.asyncio
async def test_resolve_student_unenrolled_linked_row_is_pending():
    tables = {
        "student_channels": _Query([{"student_id": "stu-physics-001"}]),
        "students": _Query([{**STUDENT, "name": "Mirco"}]),
        "enrollments": _Query([]),
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await resolve_student("tenant-demo-physics", "telegram", "555001")
    assert student is not None
    assert student["id"] is None
    assert student["phone"] == "94771234567"


@pytest.mark.asyncio
async def test_link_telegram_contact_reuses_enrolled_student():
    get_telegram_pending_store().put(
        tenant_id="tenant-demo-physics",
        chat_id="555001",
        phone="94771234567",
    )
    channel_query = _Query([])
    tables = {
        "student_channels": channel_query,
        "students": _Query([STUDENT]),
        "enrollments": _Query([{"id": "enr-1", "status": "active"}]),
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await link_telegram_contact(
            tenant_id="tenant-demo-physics",
            chat_id="555001",
            phone="+94 77 123 4567",
            display_name="Amaya",
        )

    assert student["id"] == "stu-physics-001"
    assert channel_query.upserted["channel_address"] == "555001"
    assert channel_query.upserted["channel"] == "telegram"
    assert channel_query.on_conflict == "student_id,channel"
    assert (
        get_telegram_pending_store().get(tenant_id="tenant-demo-physics", chat_id="555001")
        is None
    )


@pytest.mark.asyncio
async def test_link_telegram_contact_stores_pending_when_unknown_phone():
    tables = {
        "student_channels": _Query([]),
        "students": _Query([]),
        "enrollments": _Query([]),
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await link_telegram_contact(
            tenant_id="tenant-demo-physics",
            chat_id="555002",
            phone="94770001111",
            display_name="Nimal",
        )

    assert student["id"] is None
    assert student["phone"] == "94770001111"
    assert student.get("name") is None
    assert tables["student_channels"].upserted is None
    assert (
        get_telegram_pending_store().get(tenant_id="tenant-demo-physics", chat_id="555002")
        == "94770001111"
    )


@pytest.mark.asyncio
async def test_link_telegram_contact_does_not_link_unenrolled_stub():
    tables = {
        "student_channels": _Query([]),
        "students": _Query([{**STUDENT, "name": "Mirco"}]),
        "enrollments": _Query([]),
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await link_telegram_contact(
            tenant_id="tenant-demo-physics",
            chat_id="555003",
            phone="94771234567",
            display_name="Mirco",
        )

    assert student["id"] is None
    assert student["phone"] == "94771234567"
    assert tables["student_channels"].upserted is None
    assert (
        get_telegram_pending_store().get(tenant_id="tenant-demo-physics", chat_id="555003")
        == "94771234567"
    )


@pytest.mark.asyncio
async def test_bind_telegram_student_channel_after_enrollment():
    get_telegram_pending_store().put(
        tenant_id="tenant-demo-physics",
        chat_id="555001",
        phone="94771234567",
    )
    channel_query = _Query([])
    tables = {
        "students": _Query([STUDENT]),
        "enrollments": _Query([{"id": "enr-1", "status": "pending"}]),
        "student_channels": channel_query,
    }
    with patch("services.identity.student_resolver.get_supabase_client", return_value=_client(tables)):
        student = await bind_telegram_student_channel(
            "tenant-demo-physics",
            "555001",
            "94771234567",
        )

    assert student["id"] == "stu-physics-001"
    assert channel_query.upserted["student_id"] == "stu-physics-001"
    assert (
        get_telegram_pending_store().get(tenant_id="tenant-demo-physics", chat_id="555001")
        is None
    )
