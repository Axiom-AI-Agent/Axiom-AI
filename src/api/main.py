"""FastAPI application — Phase 2 agent framework + dev chat + Twilio webhook."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

load_dotenv(override=True)

from agents.prompts import ALL_LANGFUSE_PROMPT_NAMES
from agents.runtime import configure_agent_runtime
from api.middleware import RequestContextMiddleware
from api.routers.chat import router as chat_router
from api.routers.health import router as health_router
from api.webhooks.twilio import router as twilio_webhook_router
from infrastructure.config import validate
from infrastructure.log import setup_logging
from infrastructure.observability import flush, prefetch_prompts


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    validate(require_llm=False, require_supabase=False)
    use_mcp = os.getenv("AGENT_USE_MCP", "false").lower() == "true"
    configure_agent_runtime(use_mcp=use_mcp)
    prefetch_prompts(ALL_LANGFUSE_PROMPT_NAMES)
    app.state.startup_complete = True
    logger.info(
        "Axiom AI API ready (Phase 2 — decision graph + orchestrator; MCP={})",
        use_mcp,
    )
    yield
    flush()
    logger.info("Axiom AI API shutdown")


app = FastAPI(
    title="Axiom AI",
    description="Multi-tenant tutor agent backend",
    version="0.3.0",
    lifespan=lifespan,
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
app.include_router(twilio_webhook_router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "Axiom AI",
        "phase": 2,
        "health": "/health",
        "ready": "/ready",
        "config": "/config",
        "chat": "/chat",
        "chat_turns": "/chat/turns",
        "webhook": "/webhooks/twilio",
        "docs": "/docs",
    }
