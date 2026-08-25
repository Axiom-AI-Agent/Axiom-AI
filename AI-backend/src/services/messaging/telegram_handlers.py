"""Telegram inbound handlers — channel adapter in front of ChatPipeline."""

from __future__ import annotations

from typing import Any

from loguru import logger

from domain.enums import ChatChannel
from services.identity.student_resolver import link_telegram_contact, resolve_student
from services.messaging.pipeline import ChatPipeline
from services.messaging.schemas import ChatTurnResult, InboundMessage
from services.messaging.telegram_client import (
    resolve_telegram_file_url,
    send_telegram_contact_request,
    send_telegram_message,
)
from services.tenant_config import TenantBotTokenError, get_bot_token_for_tenant

_CONTACT_PROMPT = "To complete your registration, please share your phone number."
_VOICE_UNSUPPORTED = (
    "Voice notes aren't supported yet. Please type your message, "
    "or send a photo of your payment slip."
)
_OWN_CONTACT_ONLY = "Please share your own phone number using the button below."


async def handle_text_message(
    tenant_id: str,
    chat_id: int,
    text: str,
    from_user: dict[str, Any] | None = None,
    *,
    update_id: int | None = None,
) -> None:
    student = await resolve_student(tenant_id, ChatChannel.TELEGRAM.value, str(chat_id))
    if student is None:
        await send_telegram_contact_request(tenant_id, chat_id, _CONTACT_PROMPT)
        return

    await _run_pipeline_and_reply(
        tenant_id=tenant_id,
        chat_id=chat_id,
        student=student,
        body=text or "",
        update_id=update_id,
    )


async def handle_contact_shared(
    tenant_id: str,
    chat_id: int,
    contact: dict[str, Any],
    from_user: dict[str, Any] | None = None,
    *,
    update_id: int | None = None,
) -> None:
    sender_id = (from_user or {}).get("id")
    contact_user_id = contact.get("user_id")
    if sender_id is not None and contact_user_id is not None and sender_id != contact_user_id:
        await send_telegram_message(tenant_id, chat_id, _OWN_CONTACT_ONLY)
        await send_telegram_contact_request(tenant_id, chat_id, _CONTACT_PROMPT)
        return

    phone = contact.get("phone_number") or ""
    display_name = _display_name(contact, from_user)
    student = await link_telegram_contact(
        tenant_id=tenant_id,
        chat_id=str(chat_id),
        phone=phone,
        display_name=display_name,
    )
    await _run_pipeline_and_reply(
        tenant_id=tenant_id,
        chat_id=chat_id,
        student=student,
        body="Hello",
        update_id=update_id,
    )


async def handle_photo_message(
    tenant_id: str,
    chat_id: int,
    photo: list[dict[str, Any]],
    *,
    caption: str | None = None,
    update_id: int | None = None,
) -> None:
    student = await resolve_student(tenant_id, ChatChannel.TELEGRAM.value, str(chat_id))
    if student is None:
        await send_telegram_contact_request(tenant_id, chat_id, _CONTACT_PROMPT)
        return

    file_id = _largest_photo_file_id(photo)
    if not file_id:
        logger.warning("Telegram photo update missing file_id tenant={} chat_id={}", tenant_id, chat_id)
        return

    media_url = await resolve_telegram_file_url(tenant_id, file_id)
    await _run_pipeline_and_reply(
        tenant_id=tenant_id,
        chat_id=chat_id,
        student=student,
        body=caption or "",
        media_url=media_url,
        update_id=update_id,
    )


async def handle_voice_message(tenant_id: str, chat_id: int, voice: dict[str, Any]) -> None:
    """Voice transcription is not in this codebase yet — acknowledge without dropping."""
    del voice  # file is unused until STT lands
    await send_telegram_message(tenant_id, chat_id, _VOICE_UNSUPPORTED)


async def ensure_tenant_bot(tenant_id: str) -> None:
    """Fail fast if this webhook path does not map to a configured tenant bot."""
    await get_bot_token_for_tenant(tenant_id)


async def _run_pipeline_and_reply(
    *,
    tenant_id: str,
    chat_id: int,
    student: dict[str, Any],
    body: str,
    media_url: str | None = None,
    update_id: int | None = None,
) -> ChatTurnResult:
    phone = student.get("phone") or ""
    pipeline = ChatPipeline()
    result = await pipeline.aprocess_message(
        InboundMessage(
            channel=ChatChannel.TELEGRAM,
            tenant_id=tenant_id,
            phone=phone,
            body=body,
            media_url=media_url,
            num_media=1 if media_url else 0,
            external_id=str(update_id) if update_id is not None else str(chat_id),
        )
    )
    if result.reply:
        await send_telegram_message(tenant_id, chat_id, result.reply)
    return result


def _largest_photo_file_id(photo: list[dict[str, Any]]) -> str | None:
    if not photo:
        return None
    largest = photo[-1]
    file_id = largest.get("file_id")
    return str(file_id) if file_id else None


def _display_name(contact: dict[str, Any], from_user: dict[str, Any] | None) -> str | None:
    first = contact.get("first_name") or (from_user or {}).get("first_name") or ""
    last = contact.get("last_name") or (from_user or {}).get("last_name") or ""
    combined = f"{first} {last}".strip()
    return combined or None


def is_tenant_bot_error(exc: BaseException) -> bool:
    return isinstance(exc, TenantBotTokenError)
