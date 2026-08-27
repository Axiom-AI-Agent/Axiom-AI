"""Per-tenant Telegram bot token lookup (SRS NFR-17 — not env vars)."""

from __future__ import annotations

import time
from typing import Any

from loguru import logger

from infrastructure.db.supabase_client import get_supabase_client

_CACHE_TTL_SECONDS = 300.0
_token_cache: dict[str, tuple[float, str]] = {}


class TenantBotTokenError(ValueError):
    """Raised when a tenant has no usable Telegram bot token."""


def clear_bot_token_cache() -> None:
    """Drop cached tokens — used by tests and after rotating a token."""
    _token_cache.clear()


async def get_bot_token_for_tenant(tenant_id: str) -> str:
    """
    Return the Telegram bot token for ``tenant_id``.

    Tokens are stored on ``tenants.bot_token`` (not environment variables).
    Successful lookups are cached in-process for five minutes.
    """
    tenant_key = (tenant_id or "").strip()
    if not tenant_key:
        raise TenantBotTokenError("tenant_id is required to look up a Telegram bot token")

    cached = _token_cache.get(tenant_key)
    now = time.monotonic()
    if cached is not None:
        expires_at, token = cached
        if now < expires_at:
            return token
        _token_cache.pop(tenant_key, None)

    row = _fetch_tenant_bot_row(tenant_key)
    if not row:
        logger.error("Telegram bot token lookup failed — unknown tenant_id={}", tenant_key)
        raise TenantBotTokenError(f"Unknown tenant: {tenant_key}")

    if row.get("status") != "active":
        logger.error("Telegram bot token lookup failed — tenant {} is not active", tenant_key)
        raise TenantBotTokenError(f"Tenant is not active: {tenant_key}")

    token = (row.get("bot_token") or "").strip()
    if not token:
        logger.error("Telegram bot token missing for tenant_id={}", tenant_key)
        raise TenantBotTokenError(f"No Telegram bot token configured for tenant: {tenant_key}")

    _token_cache[tenant_key] = (now + _CACHE_TTL_SECONDS, token)
    return token


_FALLBACK_BOT_NAME = "Axiom AI"


def get_telegram_bot_display_name(tenant_id: str) -> str:
    """Return @username from the tenant row, else the institute name."""
    tenant_key = (tenant_id or "").strip()
    if not tenant_key:
        return _FALLBACK_BOT_NAME
    try:
        row = _fetch_tenant_bot_row(tenant_key) or {}
    except Exception as exc:
        logger.warning("Telegram bot name lookup failed tenant={}: {}", tenant_key, exc)
        return _FALLBACK_BOT_NAME
    username = str(row.get("telegram_bot_username") or "").strip().lstrip("@")
    if username:
        return f"@{username}"
    name = str(row.get("name") or "").strip()
    return name or _FALLBACK_BOT_NAME


def _fetch_tenant_bot_row(tenant_id: str) -> dict[str, Any] | None:
    client = get_supabase_client()
    response = (
        client.table("tenants")
        .select("id, status, bot_token, name, telegram_bot_username")
        .eq("id", tenant_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None
