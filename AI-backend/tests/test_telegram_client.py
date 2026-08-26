"""Telegram Bot API client tests — tenant token isolation."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from services.messaging.telegram_client import (
    download_telegram_file,
    get_telegram_file_path,
    send_telegram_chat_action,
    send_telegram_contact_request,
    send_telegram_message,
    telegram_api_url,
    telegram_file_url,
    telegram_typing,
)


def _json_response(payload: dict, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = payload
    response.text = str(payload)
    response.content = b""
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error",
            request=MagicMock(),
            response=response,
        )
    else:
        response.raise_for_status.return_value = None
    return response


def _async_client(response: MagicMock) -> MagicMock:
    client = AsyncMock()
    client.post.return_value = response
    client.get.return_value = response
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=client)
    cm.__aexit__ = AsyncMock(return_value=None)
    return cm, client


@pytest.mark.asyncio
async def test_send_telegram_message_uses_tenant_token():
    response = _json_response({"ok": True, "result": {"message_id": 1}})
    cm, client = _async_client(response)
    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        new_callable=AsyncMock,
        return_value="111:AAA",
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        await send_telegram_message("tenant-demo-physics", 42, "Hello")

    assert client.post.await_count == 1
    url = client.post.await_args.args[0]
    assert url == telegram_api_url("111:AAA", "sendMessage")
    assert "222:BBB" not in url
    assert client.post.await_args.kwargs["json"]["chat_id"] == 42
    assert client.post.await_args.kwargs["json"]["text"] == "Hello"


@pytest.mark.asyncio
async def test_send_telegram_message_strips_markdown_bold():
    response = _json_response({"ok": True, "result": {"message_id": 1}})
    cm, client = _async_client(response)
    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        new_callable=AsyncMock,
        return_value="111:AAA",
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        await send_telegram_message(
            "tenant-demo-physics",
            42,
            "Reply **YES** to proceed.",
        )

    assert client.post.await_args.kwargs["json"]["text"] == "Reply YES to proceed."


@pytest.mark.asyncio
async def test_send_contact_request_includes_keyboard():
    response = _json_response({"ok": True})
    cm, client = _async_client(response)
    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        new_callable=AsyncMock,
        return_value="111:AAA",
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        await send_telegram_contact_request("tenant-a", 99, "Share please")

    payload = client.post.await_args.kwargs["json"]
    button = payload["reply_markup"]["keyboard"][0][0]
    assert button["request_contact"] is True
    assert payload["text"] == "Share please"


@pytest.mark.asyncio
async def test_get_telegram_file_path():
    response = _json_response({"ok": True, "result": {"file_path": "photos/file.jpg"}})
    cm, client = _async_client(response)
    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        new_callable=AsyncMock,
        return_value="111:AAA",
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        path = await get_telegram_file_path("tenant-a", "file-1")
    assert path == "photos/file.jpg"
    assert client.get.await_args.kwargs["params"] == {"file_id": "file-1"}


@pytest.mark.asyncio
async def test_download_telegram_file_uses_matching_token():
    response = _json_response({"ok": True})
    response.content = b"image-bytes"
    cm, client = _async_client(response)
    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        new_callable=AsyncMock,
        return_value="222:BBB",
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        content = await download_telegram_file("tenant-demo-chemistry", "photos/x.jpg")
    assert content == b"image-bytes"
    assert client.get.await_args.args[0] == telegram_file_url("222:BBB", "photos/x.jpg")


@pytest.mark.asyncio
async def test_send_telegram_chat_action_uses_tenant_token():
    response = _json_response({"ok": True, "result": True})
    cm, client = _async_client(response)
    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        new_callable=AsyncMock,
        return_value="111:AAA",
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        await send_telegram_chat_action("tenant-demo-physics", 42)

    assert client.post.await_count == 1
    url = client.post.await_args.args[0]
    assert url == telegram_api_url("111:AAA", "sendChatAction")
    assert client.post.await_args.kwargs["json"] == {"chat_id": 42, "action": "typing"}


@pytest.mark.asyncio
async def test_send_telegram_chat_action_does_not_raise():
    response = _json_response({"ok": False, "description": "Forbidden"}, status_code=403)
    cm, _client = _async_client(response)
    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        new_callable=AsyncMock,
        return_value="111:AAA",
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        await send_telegram_chat_action("tenant-demo-physics", 42)


@pytest.mark.asyncio
async def test_telegram_typing_refreshes_until_released():
    calls: list[tuple[str, int]] = []
    released = asyncio.Event()

    async def _fake_action(tenant_id: str, chat_id: int, action: str = "typing") -> None:
        del action
        calls.append((tenant_id, chat_id))
        if len(calls) >= 2:
            released.set()

    with patch(
        "services.messaging.telegram_client.send_telegram_chat_action",
        new_callable=AsyncMock,
        side_effect=_fake_action,
    ), patch("services.messaging.telegram_client._TYPING_REFRESH_SECONDS", 0):
        async with telegram_typing("tenant-demo-physics", 42):
            await asyncio.wait_for(released.wait(), timeout=2)

    assert calls[0] == ("tenant-demo-physics", 42)
    assert len(calls) >= 2


@pytest.mark.asyncio
async def test_tenant_a_send_never_uses_tenant_b_token():
    calls: list[str] = []

    async def _token(tenant_id: str) -> str:
        mapping = {
            "tenant-demo-physics": "111:AAA",
            "tenant-demo-chemistry": "222:BBB",
        }
        return mapping[tenant_id]

    response = _json_response({"ok": True})
    cm, client = _async_client(response)

    async def _capture_post(url, **kwargs):
        calls.append(url)
        return response

    client.post.side_effect = _capture_post

    with patch(
        "services.messaging.telegram_client.get_bot_token_for_tenant",
        side_effect=_token,
    ), patch("services.messaging.telegram_client.httpx.AsyncClient", return_value=cm):
        await send_telegram_message("tenant-demo-physics", 1, "A")
        await send_telegram_message("tenant-demo-chemistry", 2, "B")

    assert calls[0] == telegram_api_url("111:AAA", "sendMessage")
    assert calls[1] == telegram_api_url("222:BBB", "sendMessage")
    assert "222:BBB" not in calls[0]
    assert "111:AAA" not in calls[1]
