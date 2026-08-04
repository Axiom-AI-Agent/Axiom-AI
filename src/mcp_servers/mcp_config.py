"""MCP server launch configuration."""

from __future__ import annotations

import sys
from pathlib import Path

from infrastructure.config import PROJECT_ROOT

_SRC = PROJECT_ROOT / "src"

MCP_SERVERS: dict[str, dict[str, object]] = {
    "memory": {
        "transport": "stdio",
        "command": sys.executable,
        "args": ["-m", "mcp_servers.memory_server"],
        "cwd": str(_SRC),
        "env": None,
    },
}

PHASE2_MCP_SERVERS = ("memory",)
