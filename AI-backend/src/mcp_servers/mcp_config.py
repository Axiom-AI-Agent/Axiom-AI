"""
MCP client configuration — memory + CRM + RAG (+ optional Drive).

Adapted from Week 13 ``mcp_servers/mcp_config.py`` and BookMe AI ``mcp_config.py``.

Phase 6 default: **crm + rag + memory only**. Set ``MCP_INCLUDE_DRIVE=true`` to
add the Drive subprocess (deferred for hackathon — use in-process ``DriveTool``).

MCP stdio children only inherit a small default env (HOME, PATH, …). Docker injects
secrets into the API process, not into MCP subprocesses unless forwarded here.
"""

from __future__ import annotations

import os
import sys

from loguru import logger

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
        "list_field_definitions",
        "create_enrollment",
        "commit_onboarding",
        "create_escalation",
        "resolve_escalation",
        "reject_payment_escalation",
        "kb_search",
        "kb_ingest_status",
        "get_next_class",
        "get_schedule_for_date",
        "get_week_schedule",
    }
)
MCP_DRIVE_TOOL_NAMES = frozenset({"drive_search", "drive_list"})

# App secrets forwarded to MCP stdio subprocesses (merged with MCP default PATH/HOME).
_MCP_ENV_KEYS = (
    "PYTHONPATH",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
    "SUPABASE_DB_URL",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY",
    "LANGFUSE_ENABLED",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_HOST",
    "LANGFUSE_BASE_URL",
    "LANGFUSE_PROMPT_LABEL",
    "LANGFUSE_PROMPTS",
    "DRIVE_MOCK",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "DEV_TENANT_ID",
)


def mcp_subprocess_env() -> dict[str, str]:
    """Env vars forwarded to MCP stdio child processes."""
    env: dict[str, str] = {}
    for key in _MCP_ENV_KEYS:
        val = os.environ.get(key)
        if val:
            env[key] = val
    if not env.get("SUPABASE_URL") or not env.get("SUPABASE_SERVICE_KEY"):
        logger.warning(
            "SUPABASE_URL/SUPABASE_SERVICE_KEY missing in API process — CRM MCP tools "
            "(create_escalation, get_student, …) will fail until set in container env"
        )
    return env


def mcp_include_drive() -> bool:
    return os.getenv("MCP_INCLUDE_DRIVE", "false").lower() == "true"


def _stdio_server(module: str) -> dict:
    return {
        "command": _PYTHON,
        "args": ["-m", module],
        "transport": "stdio",
        "cwd": _SRC_DIR,
        "env": mcp_subprocess_env(),
    }


def build_mcp_server_config(*, include_drive: bool | None = None) -> dict:
    """Return config for ``MultiServerMCPClient`` (BookMe / Week 13 pattern)."""
    if include_drive is None:
        include_drive = mcp_include_drive()

    config = {
        "axiom-memory": _stdio_server("mcp_servers.memory_server"),
        "axiom-crm": _stdio_server("mcp_servers.crm_server"),
        "axiom-rag": _stdio_server("mcp_servers.rag_server"),
        "axiom-schedule": _stdio_server("mcp_servers.schedule_server"),
    }
    if include_drive:
        config["axiom-drive"] = _stdio_server("mcp_servers.drive_server")
    return config


def expected_mcp_tool_names(*, include_drive: bool | None = None) -> frozenset[str]:
    names = set(MCP_CORE_TOOL_NAMES)
    if include_drive is None:
        include_drive = mcp_include_drive()
    if include_drive:
        names |= MCP_DRIVE_TOOL_NAMES
    return frozenset(names)
