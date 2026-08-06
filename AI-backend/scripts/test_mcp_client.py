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
    # Memory get_procedural returns plain text (steps or "(no procedure…)"), not JSON.
    proc_text = _text(
        await by_name["get_procedural"].ainvoke(
            {"tenant_id": "tenant-demo-physics", "name": "admissions_onboarding"}
        )
    ).strip()
    if not proc_text:
        raise SystemExit("get_procedural failed: empty response")
    print(f"get_procedural: ok ({proc_text[:80]!r}…)" if len(proc_text) > 80 else f"get_procedural: ok ({proc_text!r})")

    status_raw = await by_name["kb_ingest_status"].ainvoke({"tenant_id": "tenant-demo-physics"})
    status_text = _text(status_raw).strip()
    try:
        status_data = json.loads(status_text) if status_text.startswith("{") else {"raw": status_text}
    except json.JSONDecodeError:
        status_data = {"raw": status_text}
    print("kb_ingest_status:", status_data.get("points_count", status_data))

    close = getattr(client, "aclose", None) or getattr(client, "close", None)
    if close:
        result = close()
        if asyncio.iscoroutine(result):
            await result

    print("MCP smoke test OK")


if __name__ == "__main__":
    asyncio.run(main())
