"""Thin Telegram Bot API client — one token per tenant, never a global token."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any

import httpx
from loguru import logger

from services.messaging.plaintext import strip_markdown_markers
from services.tenant_config import get_bot_token_for_tenant

_TELEGRAM_API = "https://api.telegram.org"
_HTTP_TIMEOUT = httpx.Timeout(20.0, connect=10.0)
_DOWNLOAD_TIMEOUT = httpx.Timeout(60.0, connect=10.0)
_CHAT_ACTION_TIMEOUT = httpx.Timeout(5.0, connect=3.0)
_TYPING_REFRESH_SECONDS = 4.0
_MAX_MESSAGE_LENGTH = 4096
_CONTACT_BUTTON_TEXT = "Share my phone number"
_DEFAULT_CONTACT_PROMPT = "To complete your registration, please share your phone number."


def telegram_api_url(bot_token: str, method: str) -> str:
    return f"{_TELEGRAM_API}/bot{bot_token}/{method}"


def telegram_file_url(bot_token: str, file_path: str) -> str:
    return f"{_TELEGRAM_API}/file/bot{bot_token}/{file_path}"


def _truncate_text(text: str) -> str:
    cleaned = strip_markdown_markers(text or "")
    if len(cleaned) <= _MAX_MESSAGE_LENGTH:
        return cleaned
    return cleaned[: _MAX_MESSAGE_LENGTH - 1] + "…"


async def send_telegram_message(tenant_id: str, chat_id: int, text: str) -> dict[str, Any]:
    """Send a plain text message to a Telegram chat using that tenant's bot token."""
    bot_token = await get_bot_token_for_tenant(tenant_id)
    payload = {"chat_id": chat_id, "text": _truncate_text(text or "")}
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
        response = await client.post(telegram_api_url(bot_token, "sendMessage"), json=payload)
        _raise_telegram_error(response, tenant_id=tenant_id, method="sendMessage")
        data = response.json()
    logger.info("Sent Telegram message tenant={} chat_id={}", tenant_id, chat_id)
    return data


async def send_telegram_chat_action(
    tenant_id: str,
    chat_id: int,
    action: str = "typing",
) -> None:
    """Best-effort chat action (typing). Failures are logged, never raised."""
    try:
        bot_token = await get_bot_token_for_tenant(tenant_id)
        payload = {"chat_id": chat_id, "action": action}
        async with httpx.AsyncClient(timeout=_CHAT_ACTION_TIMEOUT) as client:
            response = await client.post(
                telegram_api_url(bot_token, "sendChatAction"),
                json=payload,
            )
            _raise_telegram_error(response, tenant_id=tenant_id, method="sendChatAction")
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.warning(
            "Telegram sendChatAction ignored tenant={} chat_id={} action={}: {}",
            tenant_id,
            chat_id,
            action,
            exc,
        )


async def _keep_telegram_typing(tenant_id: str, chat_id: int) -> None:
    while True:
        await send_telegram_chat_action(tenant_id, chat_id)
        await asyncio.sleep(_TYPING_REFRESH_SECONDS)


@asynccontextmanager
async def telegram_typing(tenant_id: str, chat_id: int) -> AsyncIterator[None]:
    """Show Telegram typing until the wrapped awaitable returns or raises."""
    task = asyncio.create_task(_keep_telegram_typing(tenant_id, chat_id))
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


async def send_telegram_contact_request(
    tenant_id: str,
    chat_id: int,
    prompt_text: str = _DEFAULT_CONTACT_PROMPT,
) -> dict[str, Any]:
    """Send a message with a one-time 'Share phone number' keyboard."""
    bot_token = await get_bot_token_for_tenant(tenant_id)
    payload = {
        "chat_id": chat_id,
        "text": _truncate_text(prompt_text),
        "reply_markup": {
            "keyboard": [[{"text": _CONTACT_BUTTON_TEXT, "request_contact": True}]],
            "one_time_keyboard": True,
            "resize_keyboard": True,
        },
    }
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
        response = await client.post(telegram_api_url(bot_token, "sendMessage"), json=payload)
        _raise_telegram_error(response, tenant_id=tenant_id, method="sendMessage")
        data = response.json()
    logger.info("Sent Telegram contact request tenant={} chat_id={}", tenant_id, chat_id)
    return data


async def get_telegram_file_path(tenant_id: str, file_id: str) -> str:
    """Resolve a Telegram file_id to a downloadable file_path via getFile."""
    bot_token = await get_bot_token_for_tenant(tenant_id)
    async with httpx.AsyncClient(timeout=_HTTP_TIMEOUT) as client:
        response = await client.get(
            telegram_api_url(bot_token, "getFile"),
            params={"file_id": file_id},
        )
        _raise_telegram_error(response, tenant_id=tenant_id, method="getFile")
        body = response.json()
    file_path = (body.get("result") or {}).get("file_path")
    if not file_path:
        raise RuntimeError(f"Telegram getFile returned no file_path for tenant {tenant_id}")
    return str(file_path)


async def download_telegram_file(tenant_id: str, file_path: str) -> bytes:
    """Download the raw bytes of a Telegram file (image or voice note)."""
    bot_token = await get_bot_token_for_tenant(tenant_id)
    url = telegram_file_url(bot_token, file_path)
    async with httpx.AsyncClient(timeout=_DOWNLOAD_TIMEOUT) as client:
        response = await client.get(url)
        _raise_telegram_error(response, tenant_id=tenant_id, method="downloadFile")
        return response.content


async def resolve_telegram_file_url(tenant_id: str, file_id: str) -> str:
    """Return a short-lived Telegram CDN URL for ``file_id`` (used as payment media_url)."""
    bot_token = await get_bot_token_for_tenant(tenant_id)
    file_path = await get_telegram_file_path(tenant_id, file_id)
    return telegram_file_url(bot_token, file_path)


def _raise_telegram_error(response: httpx.Response, *, tenant_id: str, method: str) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Telegram {} failed tenant={} status={} body={}",
            method,
            tenant_id,
            exc.response.status_code,
            exc.response.text[:300],
        )
        raise
    try:
        payload = response.json()
    except ValueError:
        return
    if isinstance(payload, dict) and payload.get("ok") is False:
        logger.error(
            "Telegram {} rejected tenant={} description={}",
            method,
            tenant_id,
            payload.get("description"),
        )
        raise RuntimeError(f"Telegram {method} failed: {payload.get('description')}")
