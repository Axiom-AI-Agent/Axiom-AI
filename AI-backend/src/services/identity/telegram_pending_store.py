"""Ephemeral Telegram chat_id → phone mapping until enrollment completes.

Not persisted. Unused mappings expire (default 24h sliding TTL) or vanish on
process restart. A student row is created only when Admissions commits enrollment.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

PENDING_TTL = timedelta(hours=24)


@dataclass
class _PendingContact:
    phone: str
    expires_at: datetime


class TelegramPendingStore:
    """Process-local store keyed by ``tenant_id:chat_id``."""

    def __init__(self, *, ttl: timedelta = PENDING_TTL) -> None:
        self._ttl = ttl
        self._by_chat: dict[str, _PendingContact] = {}

    @staticmethod
    def _key(*, tenant_id: str, chat_id: str) -> str:
        return f"{tenant_id}:{chat_id}"

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def get(self, *, tenant_id: str, chat_id: str) -> str | None:
        key = self._key(tenant_id=tenant_id, chat_id=chat_id)
        row = self._by_chat.get(key)
        if row is None:
            return None
        if self._now() >= row.expires_at:
            self._by_chat.pop(key, None)
            return None
        row.expires_at = self._now() + self._ttl
        return row.phone

    def put(self, *, tenant_id: str, chat_id: str, phone: str) -> None:
        self._purge_expired()
        self._by_chat[self._key(tenant_id=tenant_id, chat_id=chat_id)] = _PendingContact(
            phone=phone,
            expires_at=self._now() + self._ttl,
        )

    def find_chat_id_by_phone(self, *, tenant_id: str, phone: str) -> str | None:
        """Reverse lookup for staff notify before student_channels exists."""
        self._purge_expired()
        prefix = f"{tenant_id}:"
        target = phone.strip()
        if not target:
            return None
        for key, row in self._by_chat.items():
            if not key.startswith(prefix):
                continue
            if row.phone == target:
                row.expires_at = self._now() + self._ttl
                return key[len(prefix) :]
        return None

    def delete(self, *, tenant_id: str, chat_id: str) -> None:
        self._by_chat.pop(self._key(tenant_id=tenant_id, chat_id=chat_id), None)

    def clear(self) -> None:
        self._by_chat.clear()

    def _purge_expired(self) -> None:
        now = self._now()
        expired = [key for key, row in self._by_chat.items() if now >= row.expires_at]
        for key in expired:
            self._by_chat.pop(key, None)


_default_store: TelegramPendingStore | None = None


def get_telegram_pending_store() -> TelegramPendingStore:
    global _default_store
    if _default_store is None:
        _default_store = TelegramPendingStore()
    return _default_store
