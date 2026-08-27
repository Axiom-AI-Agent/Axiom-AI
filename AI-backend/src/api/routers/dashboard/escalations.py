"""Dashboard escalation inbox + staff resolve/reject."""

from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from pydantic import BaseModel

from agents.tools.crm_tool import CrmTool
from api.tenant_scope import DashboardTenant
from domain.enums import ChatChannel
from domain.escalation_reasons import is_payment_reason
from infrastructure.db.supabase_client import get_supabase_client
from services.admissions.onboarding_flow import OnboardingFlow
from services.identity.resolver import IdentityResolver
from services.messaging.persistence import MessagePersistence
from services.messaging.telegram_client import send_telegram_message
from services.messaging.twilio_client import TwilioMessagingClient

router = APIRouter(
    prefix="/escalations",
    tags=["dashboard-escalations"],
)


class EscalationActionResponse(BaseModel):
    ok: bool
    escalation_id: str
    reason_code: str
    resolution: Optional[str] = None
    enrollment_status: Optional[str] = None
    student_notified: bool = False
    notification_message: Optional[str] = None


def _telegram_chat_id_for_student(*, tenant_id: str, student_id: str | None) -> int | None:
    if not student_id:
        return None
    client = get_supabase_client()
    channel_rows = (
        client.table("student_channels")
        .select("channel_address")
        .eq("tenant_id", tenant_id)
        .eq("student_id", student_id)
        .eq("channel", ChatChannel.TELEGRAM.value)
        .limit(1)
        .execute()
        .data
        or []
    )
    if not channel_rows:
        return None
    address = channel_rows[0].get("channel_address")
    if address is None:
        return None
    try:
        return int(str(address).strip())
    except (TypeError, ValueError):
        return None


def _telegram_chat_id_for_phone(*, tenant_id: str, phone: str) -> int | None:
    """Resolve Telegram chat id from linked channels or pending contact store."""
    from services.identity.resolver import normalize_phone
    from services.identity.telegram_pending_store import get_telegram_pending_store

    student_id = _student_id_for_phone(tenant_id=tenant_id, phone=phone)
    chat_id = _telegram_chat_id_for_student(
        tenant_id=tenant_id,
        student_id=student_id,
    )
    if chat_id is not None:
        return chat_id

    normalized = normalize_phone(phone)
    pending = get_telegram_pending_store().find_chat_id_by_phone(
        tenant_id=tenant_id,
        phone=normalized,
    )
    if pending is None and normalized:
        pending = get_telegram_pending_store().find_chat_id_by_phone(
            tenant_id=tenant_id,
            phone=f"+{normalized}",
        )
    if pending is None:
        return None
    try:
        return int(str(pending).strip())
    except (TypeError, ValueError):
        return None


def _student_id_for_phone(*, tenant_id: str, phone: str) -> str | None:
    """Best-effort student lookup by normalized phone variants."""
    from services.identity.resolver import normalize_phone

    client = get_supabase_client()
    normalized = normalize_phone(phone)
    candidates = {
        normalized,
        f"+{normalized}" if normalized else "",
        normalized.lstrip("0") if normalized else "",
    }
    for candidate in candidates:
        if not candidate:
            continue
        rows = (
            client.table("students")
            .select("id")
            .eq("tenant_id", tenant_id)
            .eq("phone", candidate)
            .limit(1)
            .execute()
            .data
            or []
        )
        if rows and rows[0].get("id"):
            return str(rows[0]["id"])
    return None


async def notify_student(
    *,
    tenant_id: str,
    phone: str,
    message: str,
    intent: str = "staff_notification",
) -> bool:
    """Deliver a staff message via Telegram (preferred) or WhatsApp fallback."""
    resolver = IdentityResolver()
    persistence = MessagePersistence()

    try:
        ctx = resolver.resolve_direct(
            tenant_id=tenant_id,
            phone=phone,
        )
    except Exception as exc:
        logger.warning(
            "Staff notify identity resolve failed tenant={} phone={}: {}",
            tenant_id,
            phone,
            exc,
        )
        return False

    delivered = False
    delivery_channel = ChatChannel.HTTP_DEV

    student_id = getattr(ctx, "student_id", None) or _student_id_for_phone(
        tenant_id=tenant_id,
        phone=phone,
    )
    chat_id = _telegram_chat_id_for_student(
        tenant_id=tenant_id,
        student_id=student_id,
    )
    if chat_id is None:
        chat_id = _telegram_chat_id_for_phone(
            tenant_id=tenant_id,
            phone=phone,
        )
    if chat_id is not None:
        try:
            await send_telegram_message(tenant_id, chat_id, message)
            delivered = True
            delivery_channel = ChatChannel.TELEGRAM
        except Exception as exc:
            logger.warning(
                "Telegram staff notify failed tenant={} phone={} chat_id={}: {}",
                tenant_id,
                phone,
                chat_id,
                exc,
            )

    if not delivered:
        messaging = TwilioMessagingClient()
        result = messaging.send_whatsapp(
            to_number=phone,
            body=message,
        )
        # Treat dry_run as undelivered so demo staff get a clear failure
        # when Telegram isn't linked and Twilio isn't live.
        delivered = result.status == "sent"
        if delivered:
            delivery_channel = ChatChannel.TWILIO_WHATSAPP
        elif result.status == "dry_run":
            logger.warning(
                "WhatsApp dry-run only for tenant={} phone={}; message not sent",
                tenant_id,
                phone,
            )

    if not delivered:
        return False

    if intent == "staff_reply":
        persistence.log_staff_reply(
            ctx,
            body=message,
            channel=delivery_channel,
        )
    else:
        persistence.log_outbound(
            ctx,
            body=message,
            intent=intent,
            channel=delivery_channel,
        )

    return True


def _enrich_escalations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []
    client = get_supabase_client()
    student_ids = list({row["student_id"] for row in rows if row.get("student_id")})
    students_by_id: dict[str, dict[str, Any]] = {}
    if student_ids:
        response = (
            client.table("students")
            .select("id, name, phone")
            .in_("id", student_ids)
            .execute()
        )
        for row in response.data or []:
            students_by_id[row["id"]] = row

    enriched: list[dict[str, Any]] = []
    for row in rows:
        student = students_by_id.get(row.get("student_id", ""), {})
        enriched.append(
            {
                **row,
                "student_name": student.get("name"),
                "student_phone": student.get("phone"),
            }
        )
    return enriched


@router.get("")
async def list_escalations(
    tenant: DashboardTenant,
    status: Optional[str] = Query(None, description="open | assigned | resolved"),
    reason_code: Optional[str] = Query(None, description="payment_receipt | talk_to_tutor"),
) -> dict[str, Any]:
    """List escalations for dashboard inbox (oldest first)."""
    tenant_id = tenant.tenant_id
    client = get_supabase_client()
    query = (
        client.table("escalations")
        .select(
            "id, tenant_id, student_id, enrollment_id, reason_code, status, "
            "media_url, student_message, resolution, reviewed_by, reviewed_at, "
            "created_at, updated_at"
        )
        .eq("tenant_id", tenant_id)
    )
    if status:
        query = query.eq("status", status)
    if reason_code:
        query = query.eq("reason_code", reason_code)
    response = query.order("created_at", desc=False).execute()
    rows = _enrich_escalations(response.data or [])
    return {"tenant_id": tenant_id, "escalations": rows}


@router.patch("/{escalation_id}/resolve", response_model=EscalationActionResponse)
async def resolve_escalation(
    escalation_id: str,
    tenant: DashboardTenant,
    notify: bool = Query(True, description="Send message to student when applicable"),
    reviewed_by: Optional[str] = Query(None, description="Staff user id or email for audit"),
) -> EscalationActionResponse:
    """Approve payment (activates enrollment) or close talk-to-tutor ticket."""
    tenant_id = tenant.tenant_id
    client = get_supabase_client()
    esc = (
        client.table("escalations")
        .select("id, reason_code")
        .eq("tenant_id", tenant_id)
        .eq("id", escalation_id)
        .limit(1)
        .execute()
    )
    esc_rows = esc.data or []
    if not esc_rows:
        raise HTTPException(status_code=404, detail="Escalation not found")
    reason_code = esc_rows[0].get("reason_code", "")

    tenant_name = tenant.name or tenant.tenant_id
    tool = CrmTool()
    raw = tool.resolve_escalation(
        tenant_id=tenant_id,
        escalation_id=escalation_id,
        reviewed_by=reviewed_by,
    )
    payload = json.loads(raw)
    if not payload.get("ok"):
        raise HTTPException(status_code=400, detail=payload.get("error", "Resolve failed"))

    student = payload.get("student") or {}
    enrollment = payload.get("enrollment")
    message: str | None = None
    notified = False
    resolution = "approved" if is_payment_reason(reason_code) else "closed"

    if notify and is_payment_reason(reason_code) and student.get("phone"):
        class_row = payload.get("class") or {}
        flow = OnboardingFlow()
        message = flow.enrollment_success_message(
            student=student,
            class_row=class_row,
            tenant_name=tenant_name,
        )
        notified = await notify_student(
            tenant_id=tenant_id,
            phone=student["phone"],
            message=message,
            intent="enrollment_confirmed",
        )

    return EscalationActionResponse(
        ok=True,
        escalation_id=escalation_id,
        reason_code=reason_code,
        resolution=resolution,
        enrollment_status=(enrollment or {}).get("status") if enrollment else None,
        student_notified=notified,
        notification_message=message if notify else None,
    )


@router.patch("/{escalation_id}/reject", response_model=EscalationActionResponse)
async def reject_payment_escalation(
    escalation_id: str,
    tenant: DashboardTenant,
    notify: bool = Query(True, description="Send rejection message to student"),
    reviewed_by: Optional[str] = Query(None, description="Staff user id or email for audit"),
) -> EscalationActionResponse:
    """Reject a payment receipt — does not activate enrollment."""
    tenant_id = tenant.tenant_id
    tenant_name = tenant.name or tenant.tenant_id

    tool = CrmTool()
    raw = tool.reject_payment_escalation(
        tenant_id=tenant_id,
        escalation_id=escalation_id,
        reviewed_by=reviewed_by,
    )
    payload = json.loads(raw)
    if not payload.get("ok"):
        raise HTTPException(status_code=400, detail=payload.get("error", "Reject failed"))

    student = payload.get("student") or {}
    message: str | None = None
    notified = False

    if notify and student.get("phone"):
        flow = OnboardingFlow()
        message = flow.payment_rejected_message(student=student, tenant_name=tenant_name)
        notified = await notify_student(
            tenant_id=tenant_id,
            phone=student["phone"],
            message=message,
            intent="payment_rejected",
        )

    return EscalationActionResponse(
        ok=True,
        escalation_id=escalation_id,
        reason_code=str(payload.get("reason_code") or ""),
        resolution="rejected",
        enrollment_status=None,
        student_notified=notified,
        notification_message=message if notify else None,
    )
