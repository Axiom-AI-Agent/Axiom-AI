"""Dashboard staff → student messaging."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import DashboardChatSendRequest, DashboardChatSendResponse
from api.routers.dashboard.escalations import notify_student

router = APIRouter(prefix="/chat", tags=["dashboard-chat"])


@router.post("/send", response_model=DashboardChatSendResponse)
async def send_staff_message(body: DashboardChatSendRequest) -> DashboardChatSendResponse:
    """Staff reply to a student via WhatsApp (or dry-run log in dev)."""
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    notified = await notify_student(
        tenant_id=body.tenant_id,
        phone=body.phone,
        message=body.message.strip(),
        intent="staff_reply",
    )
    return DashboardChatSendResponse(
        ok=notified,
        tenant_id=body.tenant_id,
        phone=body.phone,
        delivered=notified,
    )
