#!/usr/bin/env python3
"""Register a Telegram bot webhook for one tenant.

Usage:
    PYTHONPATH=src python scripts/register_telegram_webhook.py <bot_token> <tenant_id> <base_url>

Example:
    PYTHONPATH=src python scripts/register_telegram_webhook.py \\
        123456:ABC-DEF tenant-demo-physics https://example.ngrok.app
"""

from __future__ import annotations

import asyncio
import sys

import httpx

_TELEGRAM_API = "https://api.telegram.org"


async def register_webhook(bot_token: str, tenant_id: str, base_url: str) -> dict:
    webhook_url = f"{base_url.rstrip('/')}/webhooks/telegram/{tenant_id}"
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(
            f"{_TELEGRAM_API}/bot{bot_token}/setWebhook",
            params={"url": webhook_url},
        )
        set_result = resp.json()
        print(set_result)

        info = await client.get(f"{_TELEGRAM_API}/bot{bot_token}/getWebhookInfo")
        info_result = info.json()
        print(info_result)
        return {"setWebhook": set_result, "getWebhookInfo": info_result}


def main() -> None:
    if len(sys.argv) != 4:
        print(
            "Usage: python scripts/register_telegram_webhook.py "
            "<bot_token> <tenant_id> <base_url>",
            file=sys.stderr,
        )
        sys.exit(1)
    asyncio.run(register_webhook(sys.argv[1], sys.argv[2], sys.argv[3]))


if __name__ == "__main__":
    main()
