"""Pending Drive file picks — list names, then resolve a numbered reply."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

PENDING_TTL = timedelta(hours=2)

_PICK_RE = re.compile(
    r"^(?:(?:no\.?|number|#)\s*)?(\d{1,2})(?:\s*(?:please|pls))?$",
    re.IGNORECASE,
)
_ORDINAL_RE = re.compile(
    r"^(?:the\s+)?(\d{1,2})(?:st|nd|rd|th)(?:\s+one)?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class DrivePickFile:
    name: str
    link: str
    folder: str = "papers"


@dataclass
class DrivePickSession:
    files: list[DrivePickFile]
    folder: str
    expires_at: datetime
    tenant_name: str = "your tuition centre"


def parse_file_pick_index(message: str) -> int | None:
    """Return a 1-based pick if the whole message is a small number / ordinal."""
    text = message.strip().lower().rstrip(".!")
    if not text:
        return None
    match = _PICK_RE.fullmatch(text) or _ORDINAL_RE.fullmatch(text)
    if match is None:
        return None
    return int(match.group(1))


def files_from_drive_payload(files: list[dict[str, Any]] | None) -> list[DrivePickFile]:
    picks: list[DrivePickFile] = []
    for item in files or []:
        name = str(item.get("name") or "file").strip() or "file"
        link = str(item.get("link") or "").strip()
        folder = str(item.get("folder") or "papers").strip() or "papers"
        picks.append(DrivePickFile(name=name, link=link, folder=folder))
    return picks


class DrivePickStore:
    """Process-local pending list keyed by tenant + session + user."""

    def __init__(self, *, ttl: timedelta = PENDING_TTL) -> None:
        self._ttl = ttl
        self._by_key: dict[str, DrivePickSession] = {}

    @staticmethod
    def _key(*, tenant_id: str, session_id: str, user_id: str) -> str:
        return f"{tenant_id}:{session_id}:{user_id}"

    def _now(self) -> datetime:
        return datetime.now(UTC)

    def get(self, *, tenant_id: str, session_id: str, user_id: str) -> DrivePickSession | None:
        key = self._key(tenant_id=tenant_id, session_id=session_id, user_id=user_id)
        row = self._by_key.get(key)
        if row is None:
            return None
        if self._now() >= row.expires_at:
            self._by_key.pop(key, None)
            return None
        return row

    def put(
        self,
        *,
        tenant_id: str,
        session_id: str,
        user_id: str,
        files: list[DrivePickFile],
        folder: str,
        tenant_name: str = "your tuition centre",
    ) -> None:
        self._purge_expired()
        self._by_key[self._key(tenant_id=tenant_id, session_id=session_id, user_id=user_id)] = DrivePickSession(
            files=list(files),
            folder=folder,
            tenant_name=tenant_name,
            expires_at=self._now() + self._ttl,
        )

    def delete(self, *, tenant_id: str, session_id: str, user_id: str) -> None:
        self._by_key.pop(self._key(tenant_id=tenant_id, session_id=session_id, user_id=user_id), None)

    def clear(self) -> None:
        self._by_key.clear()

    def _purge_expired(self) -> None:
        now = self._now()
        expired = [key for key, row in self._by_key.items() if now >= row.expires_at]
        for key in expired:
            self._by_key.pop(key, None)


_default_store: DrivePickStore | None = None


def get_drive_pick_store() -> DrivePickStore:
    global _default_store
    if _default_store is None:
        _default_store = DrivePickStore()
    return _default_store


def try_consume_drive_pick(
    *,
    message: str,
    tenant_id: str,
    session_id: str,
    user_id: str,
    store: DrivePickStore | None = None,
) -> str | None:
    """Resolve a numbered reply against the last listed Drive files.

    Returns a student-facing reply when this turn is a pick (including out of
    range). Returns None so the normal router can run when there is no pending
    list, or the message is a new question (pending list is then cleared).
    """
    pick_store = store or get_drive_pick_store()
    pending = pick_store.get(tenant_id=tenant_id, session_id=session_id, user_id=user_id)
    if pending is None or not pending.files:
        return None

    index = parse_file_pick_index(message)
    if index is None:
        pick_store.delete(tenant_id=tenant_id, session_id=session_id, user_id=user_id)
        return None

    from agents.prompts.agent_prompts import (
        build_resource_drive_list_reply,
        build_resource_drive_pick_reply,
    )

    if index < 1 or index > len(pending.files):
        return build_resource_drive_list_reply(
            files=[{"name": f.name, "folder": f.folder} for f in pending.files],
            folder=pending.folder,
            out_of_range=True,
        )

    chosen = pending.files[index - 1]
    pick_store.delete(tenant_id=tenant_id, session_id=session_id, user_id=user_id)
    return build_resource_drive_pick_reply(
        name=chosen.name,
        link=chosen.link,
        tenant_name=pending.tenant_name,
    )
