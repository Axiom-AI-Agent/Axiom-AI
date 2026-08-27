"""Resolve staff from a channel address (e.g. Telegram chat_id) and consume link codes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from loguru import logger

from domain.enums import ChatChannel
from infrastructure.db.supabase_client import get_supabase_client

LINK_CODE_RE = re.compile(r"^\s*(AXIOM-[A-F0-9]{8})\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class StaffContext:
    """Authenticated staff scope — tenant_id is never taken from message text."""

    staff_id: str
    tenant_id: str
    name: str
    role: str
    email: str | None = None
    channel_address: str | None = None


def looks_like_link_code(text: str) -> bool:
    return bool(LINK_CODE_RE.match(text or ""))


def normalize_link_code(text: str) -> str:
    match = LINK_CODE_RE.match(text or "")
    if not match:
        return ""
    return match.group(1).strip().upper()


async def resolve_staff(
    tenant_id: str,
    channel_type: str,
    channel_address: str,
) -> StaffContext | None:
    """Look up staff_channels joined to an active staff_users row for this tenant."""
    tenant = (tenant_id or "").strip()
    address = str(channel_address or "").strip()
    if not tenant or not address:
        return None

    channel = _parse_channel(channel_type)
    client = get_supabase_client()
    channel_response = (
        client.table("staff_channels")
        .select("staff_id, channel_address")
        .eq("tenant_id", tenant)
        .eq("channel", channel.value)
        .eq("channel_address", address)
        .limit(1)
        .execute()
    )
    channel_rows = channel_response.data or []
    if not channel_rows:
        return None

    staff_id = channel_rows[0].get("staff_id")
    if not staff_id:
        return None

    staff_response = (
        client.table("staff_users")
        .select("id, tenant_id, name, role, email, is_active")
        .eq("id", staff_id)
        .eq("tenant_id", tenant)
        .limit(1)
        .execute()
    )
    staff_rows = staff_response.data or []
    if not staff_rows:
        return None

    row = staff_rows[0]
    if row.get("is_active") is False:
        logger.warning(
            "Ignoring linked Telegram chat for inactive staff {} tenant={}",
            staff_id,
            tenant,
        )
        return None

    return StaffContext(
        staff_id=str(row["id"]),
        tenant_id=str(row["tenant_id"]),
        name=str(row.get("name") or "Staff"),
        role=str(row.get("role") or "viewer"),
        email=row.get("email"),
        channel_address=address,
    )


async def consume_staff_link_code(
    *,
    tenant_id: str,
    chat_id: str,
    text: str,
) -> StaffContext | None:
    """
    Bind this Telegram chat to staff if ``text`` is a valid unused code for tenant_id.

    tenant_id comes from the webhook path (the bot), never from the message.
    """
    code = normalize_link_code(text)
    tenant = (tenant_id or "").strip()
    address = str(chat_id or "").strip()
    if not code or not tenant or not address:
        return None

    client = get_supabase_client()
    now = datetime.now(timezone.utc).isoformat()
    code_response = (
        client.table("staff_link_codes")
        .select("id, tenant_id, staff_id, expires_at, consumed_at")
        .eq("tenant_id", tenant)
        .eq("code", code)
        .limit(1)
        .execute()
    )
    rows = code_response.data or []
    if not rows:
        return None

    row = rows[0]
    if row.get("consumed_at"):
        return None

    expires_at = _parse_dt(row.get("expires_at"))
    if expires_at is not None and expires_at <= datetime.now(timezone.utc):
        return None

    staff_id = row.get("staff_id")
    if not staff_id:
        return None

    staff_response = (
        client.table("staff_users")
        .select("id, tenant_id, name, role, email, is_active")
        .eq("id", staff_id)
        .eq("tenant_id", tenant)
        .limit(1)
        .execute()
    )
    staff_rows = staff_response.data or []
    if not staff_rows or staff_rows[0].get("is_active") is False:
        return None

    staff = staff_rows[0]
    existing_address = (
        client.table("staff_channels")
        .select("staff_id")
        .eq("tenant_id", tenant)
        .eq("channel", ChatChannel.TELEGRAM.value)
        .eq("channel_address", address)
        .limit(1)
        .execute()
    )
    existing_rows = existing_address.data or []
    if existing_rows and existing_rows[0].get("staff_id") != staff["id"]:
        logger.warning(
            "Telegram chat_id={} already linked to another staff tenant={}",
            address,
            tenant,
        )
        return None

    client.table("staff_channels").upsert(
        {
            "tenant_id": tenant,
            "staff_id": staff["id"],
            "channel": ChatChannel.TELEGRAM.value,
            "channel_address": address,
            "is_primary": True,
        },
        on_conflict="staff_id,channel",
    ).execute()
    client.table("staff_link_codes").update({"consumed_at": now}).eq("id", row["id"]).execute()

    logger.info(
        "Linked Telegram chat_id={} to staff {} tenant={}",
        address,
        staff["id"],
        tenant,
    )
    return StaffContext(
        staff_id=str(staff["id"]),
        tenant_id=str(staff["tenant_id"]),
        name=str(staff.get("name") or "Staff"),
        role=str(staff.get("role") or "viewer"),
        email=staff.get("email"),
        channel_address=address,
    )


def _parse_channel(channel_type: str) -> ChatChannel:
    try:
        return ChatChannel(channel_type)
    except ValueError as exc:
        raise ValueError(f"Unsupported channel_type: {channel_type}") from exc


def _parse_dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
