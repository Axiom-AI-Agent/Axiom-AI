"""FastAPI dependency injection helpers."""

from __future__ import annotations

from fastapi import HTTPException, Request


def _require_startup(request: Request) -> None:
    if not getattr(request.app.state, "startup_complete", False):
        raise HTTPException(status_code=503, detail="Service starting — try again shortly")


def get_request_id(request: Request) -> str:
    _require_startup(request)
    return getattr(request.state, "request_id", "")
