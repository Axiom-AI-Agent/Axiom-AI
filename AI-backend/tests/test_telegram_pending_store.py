"""In-memory Telegram pending contact TTL tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from services.identity.telegram_pending_store import TelegramPendingStore


def test_pending_store_expires_unused_mapping():
    store = TelegramPendingStore(ttl=timedelta(hours=24))
    store.put(tenant_id="t1", chat_id="100", phone="94770001111")
    row = store._by_chat["t1:100"]
    row.expires_at = datetime.now(UTC) - timedelta(seconds=1)

    assert store.get(tenant_id="t1", chat_id="100") is None
    assert "t1:100" not in store._by_chat


def test_pending_store_slides_ttl_on_get():
    store = TelegramPendingStore(ttl=timedelta(hours=24))
    store.put(tenant_id="t1", chat_id="100", phone="94770001111")
    first_expiry = store._by_chat["t1:100"].expires_at

    assert store.get(tenant_id="t1", chat_id="100") == "94770001111"
    assert store._by_chat["t1:100"].expires_at > first_expiry


def test_pending_store_purge_drops_expired_on_put():
    store = TelegramPendingStore(ttl=timedelta(hours=24))
    store.put(tenant_id="t1", chat_id="old", phone="94770000000")
    store._by_chat["t1:old"].expires_at = datetime.now(UTC) - timedelta(seconds=1)
    store.put(tenant_id="t1", chat_id="new", phone="94770001111")

    assert "t1:old" not in store._by_chat
    assert store.get(tenant_id="t1", chat_id="new") == "94770001111"
