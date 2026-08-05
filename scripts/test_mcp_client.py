#!/usr/bin/env python3
"""Smoke test: connect to Axiom MCP servers (crm + rag + memory; drive optional).

Adapted from BookMe AI ``scripts/test_mcp_client.py``.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)


def _text(raw) -> str:
    if isinstance(raw, list):
        return "\n".join(
            item.get("text", str(item)) for item in raw if isinstance(item, dict)
        )
    return str(raw)


async def main() -> None:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from mcp_servers.mcp_config import build_mcp_server_config, expected_mcp_tool_names

    config = build_mcp_server_config()
    print("MCP servers:", list(config.keys()))

    client = MultiServerMCPClient(config)
    tools = await client.get_tools()
    names = sorted(t.name for t in tools)
    print("Tools loaded:", names)

    expected = expected_mcp_tool_names()
    missing = expected - set(names)
    if missing:
        raise SystemExit(f"Missing tools: {sorted(missing)}")

    by_name = {t.name: t for t in tools}
    proc_raw = await by_name["get_procedural"].ainvoke(
        {"tenant_id": "tenant-demo-physics", "name": "admissions_onboarding"}
    )
    proc_data = json.loads(_text(proc_raw))
    if not proc_data.get("ok"):
        raise SystemExit(f"get_procedural failed: {proc_data}")
    print("get_procedural: ok")

    status_raw = await by_name["kb_ingest_status"].ainvoke({"tenant_id": "tenant-demo-physics"})
    status_data = json.loads(_text(status_raw))
    print("kb_ingest_status:", status_data.get("points_count", status_data))

    close = getattr(client, "aclose", None) or getattr(client, "close", None)
    if close:
        result = close()
        if asyncio.iscoroutine(result):
            await result

    print("MCP smoke test OK")


if __name__ == "__main__":
    asyncio.run(main())
