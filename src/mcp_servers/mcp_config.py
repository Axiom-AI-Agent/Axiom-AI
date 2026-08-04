"""
MCP client configuration — memory + CRM + Drive + RAG servers (Phase 4).

Adapted from Week 13 ``mcp_servers/mcp_config.py``.
"""

from __future__ import annotations

import os
import sys

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PYTHON = sys.executable


def build_mcp_server_config() -> dict:
    """Return config for MultiServerMCPClient."""
    return {
        "axiom-memory": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.memory_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
        "axiom-crm": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.crm_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
        "axiom-drive": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.drive_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
        "axiom-rag": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.rag_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
    }
