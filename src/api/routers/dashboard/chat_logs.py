"""Dashboard chat history for staff."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.schemas import ChatTurnRecord, ChatTurnsResponse
from services.identity.resolver import build_session_id, normalize_phone
from services.messaging.persistence import MessagePersistence

router = APIRouter(prefix="/chat-logs", tags=["dashboard-chat-logs"])


@router.get("", response_model=ChatTurnsResponse)
async def get_chat_logs(
    tenant_id: str = Query(..., description="Tenant ID"),
    phone: str = Query(..., description="Student phone, e.g. 94771234567"),
    limit: int = Query(default=50, ge=1, le=200),
) -> ChatTurnsResponse:
    """Fetch conversation turns for a student (same data as GET /chat/turns)."""
    session_id = build_session_id(tenant_id, normalize_phone(phone))
    persistence = MessagePersistence()
    try:
        rows = persistence.get_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=limit,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    turns = [
        ChatTurnRecord(
            id=str(row["id"]),
            role=row["role"],
            content=str(row["content"]),
            created_at=str(row["created_at"]),
        )
        for row in rows
    ]
    return ChatTurnsResponse(tenant_id=tenant_id, session_id=session_id, turns=turns)
