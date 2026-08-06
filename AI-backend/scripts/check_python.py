#!/usr/bin/env python3
"""Verify Python version meets project minimum (3.10+ for MCP adapters)."""

from __future__ import annotations

import sys

MIN_MAJOR = 3
MIN_MINOR = 10


def main() -> int:
    ok = sys.version_info >= (MIN_MAJOR, MIN_MINOR)
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if ok:
        print(f"OK Python {version} (>= {MIN_MAJOR}.{MIN_MINOR})")
        return 0
    print(
        f"WARN Python {version} — project requires >={MIN_MAJOR}.{MIN_MINOR} "
        f"(langchain-mcp-adapters / full MCP subprocess path)"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
