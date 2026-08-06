"""FastAPI dependency injection helpers."""

from __future__ import annotations

from functools import lru_cache

from fastapi import HTTPException, Request

from agents.tools.drive_tool import DriveTool
from agents.tools.rag_tool import RagTool


def _require_startup(request: Request) -> None:
    if not getattr(request.app.state, "startup_complete", False):
        raise HTTPException(status_code=503, detail="Service starting — try again shortly")


def get_request_id(request: Request) -> str:
    _require_startup(request)
    return getattr(request.state, "request_id", "")


@lru_cache(maxsize=1)
def get_rag_tool() -> RagTool:
    return RagTool()


@lru_cache(maxsize=1)
def get_drive_tool() -> DriveTool:
    return DriveTool()
