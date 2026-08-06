"""Dashboard chat history — legacy alias under /chat-logs."""

from __future__ import annotations

from fastapi import APIRouter, Query

from api.routers.dashboard.chat import get_chat_turns
from api.schemas import ChatTurnsResponse
from api.tenant_scope import DashboardTenant

router = APIRouter(prefix="/chat-logs", tags=["dashboard-chat-logs"])


@router.get("", response_model=ChatTurnsResponse)
async def get_chat_logs(
    tenant: DashboardTenant,
    phone: str = Query(..., description="Student phone, e.g. 94771234567"),
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatTurnsResponse:
    """
    Legacy path for conversation history.

    Prefer `GET /dashboard/chat/conversations/{phone}` for the full thread
    (includes student info, open escalations, and sender labels).
    """
    return await get_chat_turns(tenant=tenant, phone=phone, limit=limit)
