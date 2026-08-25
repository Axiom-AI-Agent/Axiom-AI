"""Telegram Bot API webhook router — one bot (token) per tenant."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request
from loguru import logger

from services.messaging.telegram_handlers import (
    ensure_tenant_bot,
    handle_contact_shared,
    handle_photo_message,
    handle_text_message,
    handle_voice_message,
    is_tenant_bot_error,
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/telegram/{tenant_id}")
async def telegram_webhook(tenant_id: str, request: Request) -> dict[str, bool]:
    """
    Receive Telegram updates for a single tenant bot.

    Always acknowledges with ``{"ok": True}`` so Telegram does not retry on
    handler errors. Tenant is taken from the URL path (one bot per tenant).
    """
    try:
        update = await request.json()
    except Exception:
        logger.warning("Telegram webhook received non-JSON body tenant={}", tenant_id)
        return {"ok": True}

    try:
        await ensure_tenant_bot(tenant_id)
    except Exception as exc:
        if is_tenant_bot_error(exc):
            logger.error("Telegram webhook rejected tenant={}: {}", tenant_id, exc)
        else:
            logger.exception("Telegram tenant lookup failed tenant={}", tenant_id)
        return {"ok": True}

    message = update.get("message") or {}
    chat_id = (message.get("chat") or {}).get("id")
    if chat_id is None:
        return {"ok": True}

    from_user = message.get("from") or {}
    update_id = update.get("update_id")

    try:
        await _dispatch(
            tenant_id=tenant_id,
            chat_id=int(chat_id),
            message=message,
            from_user=from_user,
            update_id=update_id if isinstance(update_id, int) else None,
        )
    except Exception:
        logger.exception(
            "Telegram handler failed tenant={} chat_id={} update_id={}",
            tenant_id,
            chat_id,
            update_id,
        )
    return {"ok": True}


async def _dispatch(
    *,
    tenant_id: str,
    chat_id: int,
    message: dict[str, Any],
    from_user: dict[str, Any],
    update_id: int | None,
) -> None:
    if "contact" in message:
        await handle_contact_shared(
            tenant_id,
            chat_id,
            message["contact"],
            from_user,
            update_id=update_id,
        )
        return

    if "photo" in message:
        await handle_photo_message(
            tenant_id,
            chat_id,
            message["photo"],
            caption=message.get("caption"),
            update_id=update_id,
        )
        return

    if "voice" in message:
        await handle_voice_message(tenant_id, chat_id, message["voice"])
        return

    if "text" in message:
        await handle_text_message(
            tenant_id,
            chat_id,
            message["text"],
            from_user,
            update_id=update_id,
        )
