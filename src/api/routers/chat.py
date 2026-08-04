"""HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from api.schemas import ChatRequest, ChatResponse, ChatTurnRecord, ChatTurnsResponse
from domain.enums import ChatChannel
from services.identity.resolver import build_session_id, normalize_phone
from services.messaging.persistence import MessagePersistence
from services.messaging.pipeline import ChatPipeline
from services.messaging.schemas import InboundMessage

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(body: ChatRequest) -> ChatResponse:
    """
    Send a student message and receive an AI reply.

    Use this during development instead of the Twilio WhatsApp sandbox.
    Messages are persisted to `message_logs` and `st_turns` exactly like WhatsApp.
    """
    pipeline = ChatPipeline()
    try:
        result = pipeline.process_message(
            InboundMessage(
                channel=ChatChannel.TWILIO_WHATSAPP,
                tenant_id=body.tenant_id,
                phone=body.phone,
                body=body.message,
                media_url=body.media_url,
                num_media=1 if body.media_url else 0,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(
        reply=result.reply,
        tenant_id=result.tenant_id,
        tenant_slug=result.tenant_slug,
        tenant_name=result.tenant_name,
        student_id=result.student_id,
        phone=result.phone,
        session_id=result.session_id,
        student_registered=result.student_registered,
    )


@router.get("/turns", response_model=ChatTurnsResponse)
async def get_chat_turns(
    tenant_id: str = Query(description="Tenant ID, e.g. tenant-demo-physics"),
    phone: str = Query(description="Student phone, e.g. 94771234567"),
    limit: int = Query(default=30, ge=1, le=100),
) -> ChatTurnsResponse:
    """Fetch recent conversation turns for a student session."""
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
