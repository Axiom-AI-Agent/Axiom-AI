"""Student channel resolution tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from domain.enums import ChatChannel
from services.identity.student_resolver import link_telegram_contact, resolve_student

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

    def execute(self):
        result = MagicMock()
        result.data = self._data
        return result


def _client(tables: dict[str, _Query]) -> MagicMock:
    client = MagicMock()
    client.table.side_effect = lambda name: tables[name]
    return client


@pytest.mark.asyncio
async def test_resolve_student_returns_linked_row():
    tables = {
        "student_channels": _Query([{"student_id": "stu-physics-001"}]),
        "students": _Query([STUDENT]),
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
async def test_link_telegram_contact_reuses_existing_student():
    channel_lookup = _Query([])
    phone_lookup = _Query([STUDENT])
    upsert_query = _Query([])
    client = MagicMock()
    client.table.side_effect = [channel_lookup, phone_lookup, upsert_query]

    with patch("services.identity.student_resolver.get_supabase_client", return_value=client):
        student = await link_telegram_contact(
            tenant_id="tenant-demo-physics",
            chat_id="555001",
            phone="+94 77 123 4567",
            display_name="Amaya",
        )

    assert student["id"] == "stu-physics-001"
    assert upsert_query.upserted["channel_address"] == "555001"
    assert upsert_query.upserted["channel"] == "telegram"
    assert upsert_query.on_conflict == "student_id,channel"


@pytest.mark.asyncio
async def test_link_telegram_contact_creates_stub_when_unknown_phone():
    channel_lookup = _Query([])
    phone_lookup = _Query([])
    insert_query = _Query([])
    upsert_query = _Query([])
    client = MagicMock()
    client.table.side_effect = [channel_lookup, phone_lookup, insert_query, upsert_query]

    with patch("services.identity.student_resolver.get_supabase_client", return_value=client):
        student = await link_telegram_contact(
            tenant_id="tenant-demo-physics",
            chat_id="555002",
            phone="94770001111",
            display_name="Nimal",
        )

    assert student["phone"] == "94770001111"
    assert student["name"] == "Nimal"
    assert insert_query.inserted["phone"] == "94770001111"
    assert upsert_query.upserted["channel_address"] == "555002"
