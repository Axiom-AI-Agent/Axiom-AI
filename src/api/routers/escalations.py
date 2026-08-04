"""Escalation inbox — staff resolve enrollment payment reviews."""

from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from agents.tools.crm_tool import CrmTool
from domain.enums import ChatChannel
from infrastructure.db.supabase_client import get_supabase_client
from services.admissions.onboarding_flow import OnboardingFlow
from services.identity.resolver import IdentityResolver
from services.messaging.persistence import MessagePersistence
from services.messaging.twilio_client import TwilioMessagingClient

router = APIRouter(prefix="/escalations", tags=["escalations"])


class EscalationResolveResponse(BaseModel):
    ok: bool
    escalation_id: str
    enrollment_status: str
    student_notified: bool
    notification_message: Optional[str] = None


async def _notify_student(
    *,
    tenant_id: str,
    phone: str,
    message: str,
) -> bool:
    resolver = IdentityResolver()
    persistence = MessagePersistence()
    messaging = TwilioMessagingClient()
    try:
        ctx = resolver.resolve_direct(tenant_id=tenant_id, phone=phone)
    except Exception:
        return False

    persistence.log_outbound(
        ctx,
        body=message,
        intent="enrollment_confirmed",
        channel=ChatChannel.HTTP_DEV,
    )
    result = messaging.send_whatsapp(
        to_number=phone,
        body=message,
    )
    return result.status in {"sent", "dry_run"}


@router.get("")
async def list_escalations(
    tenant_id: str = Query(..., description="Tenant ID"),
    status: Optional[str] = Query(None, description="open | assigned | resolved"),
) -> dict[str, Any]:
    """List escalations for dashboard inbox."""
    client = get_supabase_client()
    query = (
        client.table("escalations")
        .select(
            "id, tenant_id, student_id, enrollment_id, reason_code, status, created_at, updated_at"
        )
        .eq("tenant_id", tenant_id)
    )
    if status:
        query = query.eq("status", status)
    response = query.order("created_at", desc=True).execute()
    return {"tenant_id": tenant_id, "escalations": response.data or []}


@router.patch("/{escalation_id}/resolve", response_model=EscalationResolveResponse)
async def resolve_escalation(
    escalation_id: str,
    tenant_id: str = Query(..., description="Tenant ID"),
    notify: bool = Query(True, description="Send enrollment success message to student"),
) -> EscalationResolveResponse:
    """
    Staff approves payment review — activates pending enrollment and notifies student.
    """
    client = get_supabase_client()
    tenant_resp = (
        client.table("tenants")
        .select("id, name")
        .eq("id", tenant_id)
        .limit(1)
        .execute()
    )
    tenant_rows = tenant_resp.data or []
    tenant_name = tenant_rows[0]["name"] if tenant_rows else tenant_id

    tool = CrmTool()
    raw = tool.resolve_enrollment_escalation(
        tenant_id=tenant_id,
        escalation_id=escalation_id,
    )
    payload = json.loads(raw)
    if not payload.get("ok"):
        raise HTTPException(status_code=400, detail=payload.get("error", "Resolve failed"))

    student = payload.get("student") or {}
    class_row = payload.get("class") or {}
    flow = OnboardingFlow()
    message = flow.enrollment_success_message(
        student=student,
        class_row=class_row,
        tenant_name=tenant_name,
    )

    notified = False
    if notify and student.get("phone"):
        notified = await _notify_student(
            tenant_id=tenant_id,
            phone=student["phone"],
            message=message,
        )

    enrollment = payload.get("enrollment") or {}
    return EscalationResolveResponse(
        ok=True,
        escalation_id=escalation_id,
        enrollment_status=enrollment.get("status", "active"),
        student_notified=notified,
        notification_message=message if notify else None,
    )
