"""FastAPI application — Phase 6 integration (MCP warmup + dashboard APIs)."""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from api.rate_limit import (
    RateLimitMiddleware,
)
load_dotenv(override=True)

from agents.prompts import ALL_LANGFUSE_PROMPT_NAMES
from agents.runtime import (
    configure_agent_runtime,
    get_decision_graph,
    get_orchestrator,
    preload_agent_runtime,
    shutdown_agent_runtime,
)
from api.middleware import RequestContextMiddleware
from api.routers.chat import router as chat_router
from api.routers.classes import router as classes_router
from api.routers.dashboard.broadcast import router as dashboard_broadcast_router
from api.routers.dashboard.chat import router as dashboard_chat_router
from api.routers.dashboard.chat_logs import router as dashboard_chat_logs_router
from api.routers.dashboard.escalations import router as dashboard_escalations_router
from api.routers.dashboard.overview import router as dashboard_overview_router
from api.routers.escalations import router as escalations_router
from api.routers.health import router as health_router
from api.routers.students import router as students_router
from api.routers.tools.drive import router as drive_tools_router
from api.routers.tools.ingest import router as ingest_tools_router
from api.routers.tools.rag import router as rag_tools_router
from api.webhooks.telegram import router as telegram_webhook_router
from api.webhooks.twilio import router as twilio_webhook_router
from infrastructure.config import validate
from infrastructure.log import setup_logging
from infrastructure.observability import flush, get_langfuse_client, prefetch_prompts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Warm agent stack before accepting traffic (BookMe AI ``api/main.py`` pattern).

    Preloads decision graph + orchestrator (MCP when ``AGENT_USE_MCP=true``) so
    the first ``/chat`` request does not pay cold-start cost.
    """
    setup_logging()
    validate(require_llm=False, require_supabase=False)
    use_mcp = os.getenv("AGENT_USE_MCP", "false").lower() == "true"
    configure_agent_runtime(use_mcp=use_mcp)
    get_langfuse_client()

    decision_graph = get_decision_graph()
    orchestrator = await get_orchestrator()
    preload_agent_runtime(decision_graph=decision_graph, orchestrator=orchestrator)
    app.state.decision_graph = decision_graph
    app.state.orchestrator = orchestrator

    async def _warmup_prompts() -> None:
        try:
            await asyncio.to_thread(prefetch_prompts, ALL_LANGFUSE_PROMPT_NAMES)
        except Exception as exc:
            logger.warning("Prompt prefetch failed: {}", exc)

    async def _warmup_router() -> None:
        try:
            from agents.router import get_query_router

            await get_query_router().aroute("ping", "")
        except Exception as exc:
            logger.debug("Router warmup (non-fatal): {}", exc)

    await asyncio.gather(_warmup_prompts(), _warmup_router())
    app.state.startup_complete = True
    logger.info(
        "Axiom AI API ready (Phase 6 — MCP={}; drive MCP via MCP_INCLUDE_DRIVE)",
        use_mcp,
    )

    try:
        yield
    finally:
        logger.info("Axiom AI API shutdown")
        await shutdown_agent_runtime()
        flush()


app = FastAPI(
    title="Axiom AI",
    description="Multi-tenant tutor agent backend",
    version="0.7.0",
    lifespan=lifespan,
)
app.add_middleware(
    RateLimitMiddleware,
    default_limit=120,
    window_seconds=60,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(students_router)
app.include_router(classes_router)
app.include_router(escalations_router)
app.include_router(dashboard_escalations_router, prefix="/dashboard")
app.include_router(dashboard_chat_router, prefix="/dashboard")
app.include_router(dashboard_chat_logs_router, prefix="/dashboard")
app.include_router(dashboard_overview_router, prefix="/dashboard")
app.include_router(dashboard_broadcast_router, prefix="/dashboard")
app.include_router(rag_tools_router)
app.include_router(drive_tools_router)
app.include_router(ingest_tools_router)
app.include_router(twilio_webhook_router)
app.include_router(telegram_webhook_router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "Axiom AI",
        "phase": 6,
        "health": "/health",
        "ready": "/ready",
        "config": "/config",
        "chat": "/chat",
        "chat_turns": "/chat/turns",
        "students": "/students/{phone}",
        "classes": "/classes",
        "escalations": "/escalations",
        "dashboard_escalations": "/dashboard/escalations",
        "dashboard_escalation_resolve": "/dashboard/escalations/{id}/resolve",
        "dashboard_escalation_reject": "/dashboard/escalations/{id}/reject",
        "dashboard_overview": "/dashboard/overview",
        "dashboard_chat_conversations": "/dashboard/chat/conversations",
        "dashboard_chat_thread": "/dashboard/chat/conversations/{phone}",
        "dashboard_chat_send": "/dashboard/chat/send",
        "dashboard_chat_logs": "/dashboard/chat-logs",
        "dashboard_class_broadcast": "/dashboard/classes/{id}/broadcast",
        "dashboard_class_broadcast_recipients": "/dashboard/classes/{id}/broadcast-recipients",
        "rag_search": "/tools/rag/search",
        "drive_search": "/tools/drive/search",
        "ingest_upload": "/tools/ingest/upload",
        "webhook": "/webhooks/twilio",
        "telegram_webhook": "/webhooks/telegram/{tenant_id}",
        "docs": "/docs",
    }
