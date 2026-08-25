"""Resolve a student from a channel address (e.g. Telegram chat_id)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from loguru import logger

from domain.enums import ChatChannel
from infrastructure.db.supabase_client import get_supabase_client
from services.identity.resolver import normalize_phone


async def resolve_student(
    tenant_id: str,
    channel_type: str,
    channel_address: str,
) -> dict[str, Any] | None:
    """
    Look up student_channels joined to students.

    Returns the student row if this channel address is already linked, else None.
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
    if not channel_rows:
        return None

    student_id = channel_rows[0].get("student_id")
    if not student_id:
        return None

    student_response = (
        client.table("students")
        .select("id, tenant_id, name, phone, school, district, consent_at, language_pref")
        .eq("tenant_id", tenant_id)
        .eq("id", student_id)
        .limit(1)
        .execute()
    )
    student_rows = student_response.data or []
    return student_rows[0] if student_rows else None


async def link_telegram_contact(
    *,
    tenant_id: str,
    chat_id: str,
    phone: str,
    display_name: str | None = None,
) -> dict[str, Any]:
    """
    Bind a Telegram chat_id to a student identified by phone.

    Creates a stub student row when none exists yet so Admissions can continue
    via the existing ChatPipeline (student_exists=False until onboarding completes).
    """
    normalized_phone = normalize_phone(phone)
    if not normalized_phone:
        raise ValueError("A phone number is required to link a Telegram contact")

    address = str(chat_id).strip()
    existing_channel = await resolve_student(tenant_id, ChatChannel.TELEGRAM.value, address)
    if existing_channel and existing_channel.get("phone") == normalized_phone:
        return existing_channel

    student = _lookup_student_by_phone(tenant_id, normalized_phone)
    if student is None:
        student = _insert_stub_student(
            tenant_id=tenant_id,
            phone=normalized_phone,
            name=(display_name or "").strip() or None,
        )
        logger.info(
            "Created stub student {} for Telegram contact tenant={} phone={}",
            student["id"],
            tenant_id,
            normalized_phone,
        )

    _upsert_channel(
        tenant_id=tenant_id,
        student_id=student["id"],
        channel=ChatChannel.TELEGRAM,
        channel_address=address,
    )
    logger.info(
        "Linked Telegram chat_id={} to student {} tenant={}",
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


def _lookup_student_by_phone(tenant_id: str, phone: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    response = (
        client.table("students")
        .select("id, tenant_id, name, phone, school, district, consent_at, language_pref")
        .eq("tenant_id", tenant_id)
        .eq("phone", phone)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def _insert_stub_student(*, tenant_id: str, phone: str, name: str | None) -> dict[str, Any]:
    student_id = f"stu-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC).isoformat()
    payload: dict[str, Any] = {
        "id": student_id,
        "tenant_id": tenant_id,
        "phone": phone,
        "updated_at": now,
    }
    if name:
        payload["name"] = name

    client = get_supabase_client()
    response = client.table("students").insert(payload).execute()
    rows = response.data or []
    return rows[0] if rows else payload


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
