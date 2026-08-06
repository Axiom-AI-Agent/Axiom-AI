"""
MCP client configuration — memory + CRM + RAG (+ optional Drive).

Adapted from Week 13 ``mcp_servers/mcp_config.py`` and BookMe AI ``mcp_config.py``.

Phase 6 default: **crm + rag + memory only**. Set ``MCP_INCLUDE_DRIVE=true`` to
add the Drive subprocess (deferred for hackathon — use in-process ``DriveTool``).
"""

from __future__ import annotations

import os
import sys

_SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PYTHON = sys.executable

# Tool names exposed by each server (used by /ready and smoke tests).
MCP_CORE_TOOL_NAMES = frozenset(
    {
        "recall_turns",
        "add_turn",
        "get_procedural",
        "get_student",
        "register_student",
        "list_classes",
        "get_tenant_info",
        "get_class_details",
        "list_staff",
        "create_enrollment",
        "commit_onboarding",
        "create_escalation",
        "resolve_escalation",
        "reject_payment_escalation",
        "kb_search",
        "kb_ingest_status",
    }
)
MCP_DRIVE_TOOL_NAMES = frozenset({"drive_search", "drive_list"})


def mcp_include_drive() -> bool:
    return os.getenv("MCP_INCLUDE_DRIVE", "false").lower() == "true"


def build_mcp_server_config(*, include_drive: bool | None = None) -> dict:
    """Return config for ``MultiServerMCPClient`` (BookMe / Week 13 pattern)."""
    if include_drive is None:
        include_drive = mcp_include_drive()

    config = {
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
        "axiom-rag": {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.rag_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        },
    }
    if include_drive:
        config["axiom-drive"] = {
            "command": _PYTHON,
            "args": ["-m", "mcp_servers.drive_server"],
            "transport": "stdio",
            "cwd": _SRC_DIR,
        }
    return config


def expected_mcp_tool_names(*, include_drive: bool | None = None) -> frozenset[str]:
    names = set(MCP_CORE_TOOL_NAMES)
    if include_drive is None:
        include_drive = mcp_include_drive()
    if include_drive:
        names |= MCP_DRIVE_TOOL_NAMES
    return frozenset(names)
