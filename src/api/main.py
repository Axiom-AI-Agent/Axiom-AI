"""FastAPI application — Phase 0 foundation."""

from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

load_dotenv(override=True)

from api.middleware import RequestContextMiddleware
from api.routers.health import router as health_router
from infrastructure.config import validate
from infrastructure.log import setup_logging
from infrastructure.observability import flush


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    validate(require_llm=False, require_supabase=False)
    app.state.startup_complete = True
    logger.info("Axiom AI API ready (Phase 0 — foundation)")
    yield
    flush()
    logger.info("Axiom AI API shutdown")


app = FastAPI(
    title="Axiom AI",
    description="Multi-tenant tutor agent backend",
    version="0.1.0",
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


@app.get("/")
async def root() -> dict:
    return {
        "service": "Axiom AI",
        "phase": 0,
        "health": "/health",
        "ready": "/ready",
        "config": "/config",
        "docs": "/docs",
    }
