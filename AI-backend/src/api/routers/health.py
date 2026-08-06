"""Health, readiness, and config endpoints."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Request

from api.schemas import ConfigResponse, HealthResponse, ReadinessCheck, ReadinessResponse
from infrastructure.config import (
    CHAT_MODEL,
    CHAT_PROVIDER,
    GUARDRAIL_MODEL,
    GUARDRAIL_PROVIDER,
    LANGFUSE_PROMPT_LABEL,
    MERGE_MODEL,
    MERGE_PROVIDER,
    MESSAGING_DRY_RUN,
    PROVIDER,
    QDRANT_API_KEY,
    QDRANT_URL,
    ROUTER_MODEL,
    ROUTER_PROVIDER,
    SUPABASE_SERVICE_KEY,
    SUPABASE_URL,
    langfuse_configured,
    validate,
)
from infrastructure.observability import is_langfuse_enabled
from infrastructure.db.supabase_client import ping_supabase

router = APIRouter(tags=["System"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    started = getattr(request.app.state, "startup_complete", False)
    return HealthResponse(status="ok" if started else "starting", phase=6)


@router.get("/ready", response_model=ReadinessResponse)
async def ready(request: Request) -> ReadinessResponse:
    if not getattr(request.app.state, "startup_complete", False):
        return ReadinessResponse(
            ready=False,
            checks=[ReadinessCheck(name="startup", ok=False, detail="not initialised")],
        )

    async def check_config() -> ReadinessCheck:
        try:
            await asyncio.to_thread(validate, require_llm=False, require_supabase=False)
            return ReadinessCheck(name="config", ok=True)
        except Exception as exc:
            return ReadinessCheck(name="config", ok=False, detail=str(exc)[:200])

    async def check_supabase() -> ReadinessCheck:
        ok, detail = await asyncio.to_thread(ping_supabase)
        return ReadinessCheck(name="supabase", ok=ok, detail=detail)

    async def check_qdrant() -> ReadinessCheck:
        configured = bool(QDRANT_URL and QDRANT_API_KEY)
        return ReadinessCheck(
            name="qdrant",
            ok=configured,
            detail="configured" if configured else "QDRANT_URL/API_KEY optional until Phase 4",
        )

    async def check_langfuse() -> ReadinessCheck:
        configured = langfuse_configured()
        active = is_langfuse_enabled()
        if not configured:
            return ReadinessCheck(
                name="langfuse",
                ok=True,
                detail="optional until keys set",
            )
        return ReadinessCheck(
            name="langfuse",
            ok=active,
            detail="connected" if active else "keys invalid or disabled — local prompt fallbacks",
        )

    async def check_mcp(request: Request) -> ReadinessCheck:
        orchestrator = getattr(request.app.state, "orchestrator", None)
        if orchestrator is None:
            return ReadinessCheck(name="mcp", ok=False, detail="orchestrator not initialised")
        tools = getattr(orchestrator, "mcp_tools", None)
        if not tools:
            return ReadinessCheck(name="mcp", ok=True, detail="in-process tools (no MCP subprocess)")
        from mcp_servers.mcp_config import expected_mcp_tool_names

        expected = expected_mcp_tool_names()
        loaded = set(tools.keys())
        missing = sorted(expected - loaded)
        if missing:
            return ReadinessCheck(
                name="mcp",
                ok=False,
                detail=f"missing tools: {', '.join(missing[:8])}",
            )
        return ReadinessCheck(
            name="mcp",
            ok=True,
            detail=f"{len(loaded)} tools ({', '.join(sorted(loaded)[:6])}…)",
        )

    checks = list(
        await asyncio.gather(
            check_config(),
            check_supabase(),
            check_qdrant(),
            check_langfuse(),
            check_mcp(request),
        )
    )
    # Phase 0: ready when startup + config OK; Supabase required for full ready in prod
    core_ready = all(c.ok for c in checks if c.name in ("config", "startup"))
    supabase_ok = next((c.ok for c in checks if c.name == "supabase"), False)
    return ReadinessResponse(ready=core_ready and supabase_ok, checks=checks)


@router.get("/config", response_model=ConfigResponse)
async def active_config() -> ConfigResponse:
    return ConfigResponse(
        provider=PROVIDER,
        router_model=ROUTER_MODEL,
        router_provider=ROUTER_PROVIDER,
        guardrail_model=GUARDRAIL_MODEL,
        guardrail_provider=GUARDRAIL_PROVIDER,
        chat_model=CHAT_MODEL,
        chat_provider=CHAT_PROVIDER,
        merge_model=MERGE_MODEL,
        merge_provider=MERGE_PROVIDER,
        messaging_dry_run=MESSAGING_DRY_RUN,
        supabase_configured=bool(SUPABASE_URL and SUPABASE_SERVICE_KEY),
        qdrant_configured=bool(QDRANT_URL and QDRANT_API_KEY),
        langfuse_configured=langfuse_configured(),
        langfuse_prompt_label=LANGFUSE_PROMPT_LABEL,
    )
