"""Supabase REST client wrapper."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from loguru import logger

from infrastructure.config import SUPABASE_SERVICE_KEY, SUPABASE_URL

_client = None


@lru_cache(maxsize=1)
def get_supabase_client():
    """Return a singleton Supabase client (requires service role key)."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
    from supabase import create_client

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def ping_supabase() -> tuple[bool, str]:
    """Lightweight connectivity check via tenants table."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return False, "SUPABASE_URL or SUPABASE_SERVICE_KEY missing"
    try:
        client = get_supabase_client()
        client.table("tenants").select("id").limit(1).execute()
        return True, "connected"
    except Exception as exc:
        logger.debug("Supabase ping failed: {}", exc)
        return False, str(exc)[:200]


def list_tenants(limit: int = 10) -> list[dict[str, Any]]:
    client = get_supabase_client()
    response = client.table("tenants").select("*").limit(limit).execute()
    return response.data or []
