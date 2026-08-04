"""
MCP client configuration — memory server only for Phase 2.

Adapted from Week 13 ``mcp_servers/mcp_config.py`` (CRM/RAG/CAG servers deferred).
"""

from __future__ import annotations

import os
import sys

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PYTHON = sys.executable


def build_mcp_server_config() -> dict:
    """Return config for MultiServerMCPClient (memory_server only in Phase 2)."""
    return {
        "axiom-memory": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.memory_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
    }
