"""Fan out a staff class announcement to Telegram-linked students."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from loguru import logger

from domain.enums import ChatChannel
from infrastructure.db.supabase_client import get_supabase_client
from services.admissions.admissions_db_client import AdmissionsDbClient
from services.identity.context import IdentityContext
from services.identity.resolver import build_session_id, normalize_phone
from services.messaging.persistence import MessagePersistence
from services.messaging.telegram_client import send_telegram_message

_ENROLLED_STATUSES = frozenset({"active", "pending"})
_SEND_CONCURRENCY = 20


class ClassNotFoundError(Exception):
    """Raised when a class does not exist for the given tenant."""

    def __init__(self, class_id: str) -> None:
        self.class_id = class_id
        super().__init__(f"Class not found: {class_id}")


@dataclass(frozen=True)
class BroadcastRecipient:
    student_id: str
    name: str
    phone: str
    chat_id: int


@dataclass(frozen=True)
class BroadcastAudience:
    class_id: str
    class_name: str
    enrolled: int
    reachable: tuple[BroadcastRecipient, ...]
    skipped_no_telegram: int

    @property
    def reachable_names(self) -> list[str]:
        return [_first_name(recipient.name) for recipient in self.reachable]


@dataclass(frozen=True)
class BroadcastFailure:
    student_id: str
    name: str


@dataclass(frozen=True)
class BroadcastResult:
    sent: int
    failed: int
    skipped_no_telegram: int
    failures: tuple[BroadcastFailure, ...]


def class_display_name(subject_class: dict[str, Any]) -> str:
    return str(subject_class.get("name") or subject_class.get("subject") or "your class")


def format_announcement(class_name: str, message: str) -> str:
    return f"Class announcement — {class_name}\n\n{message.strip()}"


def resolve_broadcast_audience(*, tenant_id: str, class_id: str) -> BroadcastAudience:
    """Return reachable Telegram students for a class (active or pending enrollment)."""
    db = AdmissionsDbClient()
    subject_class = db.get_class(tenant_id=tenant_id, class_id=class_id)
    if subject_class is None:
        raise ClassNotFoundError(class_id)

    enrollments = _list_class_enrollments(tenant_id=tenant_id, class_id=class_id)
    student_ids = [row["student_id"] for row in enrollments if row.get("student_id")]
    students = _fetch_students(tenant_id=tenant_id, student_ids=student_ids)
    channels = _fetch_telegram_channels(tenant_id=tenant_id, student_ids=student_ids)

    reachable: list[BroadcastRecipient] = []
    skipped = 0
    seen: set[str] = set()

    for student_id in student_ids:
        if student_id in seen:
            continue
        seen.add(student_id)

        student = students.get(student_id) or {}
        chat_id = _parse_chat_id(channels.get(student_id))
        if chat_id is None:
            skipped += 1
            continue

        phone = normalize_phone(str(student.get("phone") or ""))
        reachable.append(
            BroadcastRecipient(
                student_id=student_id,
                name=str(student.get("name") or "").strip() or "Student",
                phone=phone,
                chat_id=chat_id,
            )
        )

    return BroadcastAudience(
        class_id=class_id,
        class_name=class_display_name(subject_class),
        enrolled=len(seen),
        reachable=tuple(reachable),
        skipped_no_telegram=skipped,
    )


async def send_class_broadcast(
    *,
    tenant_id: str,
    class_id: str,
    message: str,
) -> BroadcastResult:
    audience = resolve_broadcast_audience(tenant_id=tenant_id, class_id=class_id)
    text = format_announcement(audience.class_name, message)
    if not audience.reachable:
        return BroadcastResult(
            sent=0,
            failed=0,
            skipped_no_telegram=audience.skipped_no_telegram,
            failures=(),
        )

    persistence = MessagePersistence()
    semaphore = asyncio.Semaphore(_SEND_CONCURRENCY)

    async def _deliver(recipient: BroadcastRecipient) -> BroadcastFailure | None:
        async with semaphore:
            try:
                await send_telegram_message(tenant_id, recipient.chat_id, text)
            except Exception as exc:
                logger.warning(
                    "Class broadcast send failed tenant={} class={} student={}: {}",
                    tenant_id,
                    class_id,
                    recipient.student_id,
                    exc,
                )
                return BroadcastFailure(student_id=recipient.student_id, name=recipient.name)

            _log_staff_reply(persistence, tenant_id=tenant_id, recipient=recipient, body=text)
            return None

    outcomes = await asyncio.gather(*[_deliver(recipient) for recipient in audience.reachable])
    failures = tuple(item for item in outcomes if item is not None)
    sent = len(audience.reachable) - len(failures)
    return BroadcastResult(
        sent=sent,
        failed=len(failures),
        skipped_no_telegram=audience.skipped_no_telegram,
        failures=failures,
    )


def _log_staff_reply(
    persistence: MessagePersistence,
    *,
    tenant_id: str,
    recipient: BroadcastRecipient,
    body: str,
) -> None:
    if not recipient.phone:
        logger.warning(
            "Skipping broadcast chat log tenant={} student={} (missing phone)",
            tenant_id,
            recipient.student_id,
        )
        return

    ctx = IdentityContext(
        tenant_id=tenant_id,
        tenant_slug=None,
        tenant_name=None,
        phone=recipient.phone,
        session_id=build_session_id(tenant_id, recipient.phone),
        student_id=recipient.student_id,
        student_exists=True,
        student_name=recipient.name,
    )
    try:
        persistence.log_staff_reply(ctx, body=body, channel=ChatChannel.TELEGRAM)
    except Exception as exc:
        logger.warning(
            "Failed to log class broadcast tenant={} student={}: {}",
            tenant_id,
            recipient.student_id,
            exc,
        )


def _list_class_enrollments(*, tenant_id: str, class_id: str) -> list[dict[str, Any]]:
    client = get_supabase_client()
    response = (
        client.table("enrollments")
        .select("student_id, status")
        .eq("tenant_id", tenant_id)
        .eq("class_id", class_id)
        .in_("status", list(_ENROLLED_STATUSES))
        .execute()
    )
    rows = response.data or []
    return [row for row in rows if row.get("status") in _ENROLLED_STATUSES]


def _fetch_students(*, tenant_id: str, student_ids: list[str]) -> dict[str, dict[str, Any]]:
    unique_ids = list(dict.fromkeys(student_ids))
    if not unique_ids:
        return {}
    client = get_supabase_client()
    response = (
        client.table("students")
        .select("id, name, phone")
        .eq("tenant_id", tenant_id)
        .in_("id", unique_ids)
        .execute()
    )
    return {row["id"]: row for row in (response.data or []) if row.get("id")}


def _fetch_telegram_channels(*, tenant_id: str, student_ids: list[str]) -> dict[str, str]:
    unique_ids = list(dict.fromkeys(student_ids))
    if not unique_ids:
        return {}
    client = get_supabase_client()
    response = (
        client.table("student_channels")
        .select("student_id, channel_address")
        .eq("tenant_id", tenant_id)
        .eq("channel", ChatChannel.TELEGRAM.value)
        .in_("student_id", unique_ids)
        .execute()
    )
    mapping: dict[str, str] = {}
    for row in response.data or []:
        student_id = row.get("student_id")
        address = row.get("channel_address")
        if student_id and address is not None:
            mapping[str(student_id)] = str(address)
    return mapping


def _parse_chat_id(address: str | None) -> int | None:
    if address is None:
        return None
    try:
        return int(str(address).strip())
    except (TypeError, ValueError):
        return None


def _first_name(name: str) -> str:
    cleaned = name.strip()
    if not cleaned:
        return "Student"
    return cleaned.split()[0]
