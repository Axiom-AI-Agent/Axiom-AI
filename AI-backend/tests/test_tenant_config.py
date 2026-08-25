"""Per-tenant Telegram bot token lookup tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from services.tenant_config import (
    TenantBotTokenError,
    clear_bot_token_cache,
    get_bot_token_for_tenant,
)


def _tenant_client(row: dict | None) -> MagicMock:
    result = MagicMock()
    result.data = [row] if row else []
    query = MagicMock()
    query.select.return_value = query
    query.eq.return_value = query
    query.limit.return_value = query
    query.execute.return_value = result
    client = MagicMock()
    client.table.return_value = query
    return client


@pytest.fixture(autouse=True)
def _reset_cache():
    clear_bot_token_cache()
    yield
    clear_bot_token_cache()


@pytest.mark.asyncio
async def test_get_bot_token_for_tenant_returns_token():
    client = _tenant_client(
        {"id": "tenant-demo-physics", "status": "active", "bot_token": "111:AAA"}
    )
    with patch("services.tenant_config.get_supabase_client", return_value=client):
        token = await get_bot_token_for_tenant("tenant-demo-physics")
    assert token == "111:AAA"


@pytest.mark.asyncio
async def test_get_bot_token_for_tenant_uses_cache():
    client = _tenant_client(
        {"id": "tenant-demo-physics", "status": "active", "bot_token": "111:AAA"}
    )
    with patch("services.tenant_config.get_supabase_client", return_value=client):
        first = await get_bot_token_for_tenant("tenant-demo-physics")
        second = await get_bot_token_for_tenant("tenant-demo-physics")
    assert first == second == "111:AAA"
    assert client.table.call_count == 1


@pytest.mark.asyncio
async def test_get_bot_token_missing_tenant_raises():
    client = _tenant_client(None)
    with (
        patch("services.tenant_config.get_supabase_client", return_value=client),
        pytest.raises(TenantBotTokenError, match="Unknown tenant"),
    ):
        await get_bot_token_for_tenant("missing")


@pytest.mark.asyncio
async def test_get_bot_token_missing_token_raises():
    client = _tenant_client({"id": "tenant-demo-physics", "status": "active", "bot_token": ""})
    with (
        patch("services.tenant_config.get_supabase_client", return_value=client),
        pytest.raises(TenantBotTokenError, match="No Telegram bot token"),
    ):
        await get_bot_token_for_tenant("tenant-demo-physics")


@pytest.mark.asyncio
async def test_get_bot_token_inactive_tenant_raises():
    client = _tenant_client(
        {"id": "tenant-demo-physics", "status": "suspended", "bot_token": "111:AAA"}
    )
    with (
        patch("services.tenant_config.get_supabase_client", return_value=client),
        pytest.raises(TenantBotTokenError, match="not active"),
    ):
        await get_bot_token_for_tenant("tenant-demo-physics")


@pytest.mark.asyncio
async def test_tokens_are_isolated_per_tenant():
    physics = _tenant_client(
        {"id": "tenant-demo-physics", "status": "active", "bot_token": "111:AAA"}
    )
    chemistry = _tenant_client(
        {"id": "tenant-demo-chemistry", "status": "active", "bot_token": "222:BBB"}
    )

    with patch(
        "services.tenant_config.get_supabase_client",
        side_effect=[physics, chemistry],
    ):
        assert await get_bot_token_for_tenant("tenant-demo-physics") == "111:AAA"
        assert await get_bot_token_for_tenant("tenant-demo-chemistry") == "222:BBB"
