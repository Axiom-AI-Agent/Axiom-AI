"""Resolve a student from a channel address (e.g. Telegram chat_id)."""

from __future__ import annotations

from typing import Any

from loguru import logger

from domain.enums import ChatChannel
from infrastructure.db.supabase_client import get_supabase_client
from services.identity.resolver import normalize_phone
from services.identity.telegram_pending_store import get_telegram_pending_store

_ENROLLED_STATUSES = frozenset({"active", "pending"})


async def resolve_student(
    tenant_id: str,
    channel_type: str,
    channel_address: str,
) -> dict[str, Any] | None:
    """
    Look up student_channels joined to students, or a pending Telegram phone.

    Returns the student row if this channel address is already linked, a
    phone-only identity if the chat shared a number but is not enrolled yet,
    else None.
    """
    channel = _parse_channel(channel_type)
    address = str(channel_address).strip()
    if not tenant_id or not address:
        return None

    client = get_supabase_client()
    channel_response = (
        client.table("student_channels")
        .select("student_id")
        .eq("tenant_id", tenant_id)
        .eq("channel", channel.value)
        .eq("channel_address", address)
        .limit(1)
        .execute()
    )
    channel_rows = channel_response.data or []
    if channel_rows:
        student_id = channel_rows[0].get("student_id")
        if student_id:
            student_response = (
                client.table("students")
                .select(
                    "id, tenant_id, name, phone, school, district, extra_fields, "
                    "consent_at, language_pref"
                )
                .eq("tenant_id", tenant_id)
                .eq("id", student_id)
                .limit(1)
                .execute()
            )
            student_rows = student_response.data or []
            if student_rows:
                student = student_rows[0]
                if _has_enrollment(tenant_id, student["id"]):
                    return student
                phone = student.get("phone")
                if phone:
                    return _pending_identity(tenant_id, str(phone))

    if channel is ChatChannel.TELEGRAM:
        pending_phone = _lookup_pending_phone(tenant_id, address)
        if pending_phone:
            return _pending_identity(tenant_id, pending_phone)

    return None


async def link_telegram_contact(
    *,
    tenant_id: str,
    chat_id: str,
    phone: str,
    display_name: str | None = None,
) -> dict[str, Any]:
    """
    Bind a Telegram chat_id to a phone number.

    Enrolled students are linked on student_channels immediately. Everyone else
    is remembered in process memory (24h sliding TTL) so ChatPipeline sees
    student_exists=False and Admissions can run the normal enrollment flow.
    display_name is unused — the student's legal name is collected during onboarding.
    """
    del display_name
    normalized_phone = normalize_phone(phone)
    if not normalized_phone:
        raise ValueError("A phone number is required to link a Telegram contact")

    address = str(chat_id).strip()
    existing = await resolve_student(tenant_id, ChatChannel.TELEGRAM.value, address)
    if existing and existing.get("id") and existing.get("phone") == normalized_phone:
        if _has_enrollment(tenant_id, existing["id"]):
            return existing

    student = _lookup_student_by_phone(tenant_id, normalized_phone)
    if student and _has_enrollment(tenant_id, student["id"]):
        _upsert_channel(
            tenant_id=tenant_id,
            student_id=student["id"],
            channel=ChatChannel.TELEGRAM,
            channel_address=address,
        )
        _delete_pending(tenant_id, address)
        logger.info(
            "Linked Telegram chat_id={} to enrolled student {} tenant={}",
            address,
            student["id"],
            tenant_id,
        )
        return student

    _upsert_pending(tenant_id=tenant_id, chat_id=address, phone=normalized_phone)
    logger.info(
        "Stored pending Telegram contact chat_id={} tenant={} phone={}",
        address,
        tenant_id,
        normalized_phone,
    )
    return _pending_identity(tenant_id, normalized_phone)


async def bind_telegram_student_channel(
    tenant_id: str,
    chat_id: str,
    phone: str,
) -> dict[str, Any] | None:
    """If Admissions created/enrolled this phone, attach student_channels."""
    normalized_phone = normalize_phone(phone)
    address = str(chat_id).strip()
    if not tenant_id or not normalized_phone or not address:
        return None

    student = _lookup_student_by_phone(tenant_id, normalized_phone)
    if student is None or not _has_enrollment(tenant_id, student["id"]):
        return None

    _upsert_channel(
        tenant_id=tenant_id,
        student_id=student["id"],
        channel=ChatChannel.TELEGRAM,
        channel_address=address,
    )
    _delete_pending(tenant_id, address)
    logger.info(
        "Bound Telegram chat_id={} to student {} tenant={} after enrollment",
        address,
        student["id"],
        tenant_id,
    )
    return student


def _parse_channel(channel_type: str) -> ChatChannel:
    try:
        return ChatChannel(channel_type)
    except ValueError as exc:
        raise ValueError(f"Unsupported channel_type: {channel_type}") from exc


def _pending_identity(tenant_id: str, phone: str) -> dict[str, Any]:
    return {
        "id": None,
        "tenant_id": tenant_id,
        "name": None,
        "phone": phone,
    }


def _lookup_student_by_phone(tenant_id: str, phone: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    response = (
        client.table("students")
        .select(
            "id, tenant_id, name, phone, school, district, extra_fields, "
            "consent_at, language_pref"
        )
        .eq("tenant_id", tenant_id)
        .eq("phone", phone)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def _has_enrollment(tenant_id: str, student_id: str) -> bool:
    client = get_supabase_client()
    response = (
        client.table("enrollments")
        .select("id, status")
        .eq("tenant_id", tenant_id)
        .eq("student_id", student_id)
        .execute()
    )
    return any(
        row.get("status") in _ENROLLED_STATUSES for row in (response.data or [])
    )


def _lookup_pending_phone(tenant_id: str, chat_id: str) -> str | None:
    return get_telegram_pending_store().get(tenant_id=tenant_id, chat_id=chat_id)


def _upsert_pending(*, tenant_id: str, chat_id: str, phone: str) -> None:
    get_telegram_pending_store().put(tenant_id=tenant_id, chat_id=chat_id, phone=phone)


def _delete_pending(tenant_id: str, chat_id: str) -> None:
    get_telegram_pending_store().delete(tenant_id=tenant_id, chat_id=chat_id)


def _upsert_channel(
    *,
    tenant_id: str,
    student_id: str,
    channel: ChatChannel,
    channel_address: str,
) -> None:
    client = get_supabase_client()
    client.table("student_channels").upsert(
        {
            "tenant_id": tenant_id,
            "student_id": student_id,
            "channel": channel.value,
            "channel_address": channel_address,
            "is_primary": True,
        },
        on_conflict="student_id,channel",
    ).execute()
