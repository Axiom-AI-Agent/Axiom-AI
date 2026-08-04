"""Dashboard overview stats for staff home screen."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from api.tenant_scope import DashboardTenant
from domain.escalation_reasons import PAYMENT_RECEIPT, TALK_TO_TUTOR
from infrastructure.db.supabase_client import get_supabase_client

router = APIRouter(prefix="/overview", tags=["dashboard-overview"])


def _count_rows(table: str, *, tenant_id: str, filters: dict[str, str] | None = None) -> int:
    client = get_supabase_client()
    query = client.table(table).select("id", count="exact").eq("tenant_id", tenant_id)
    for key, value in (filters or {}).items():
        query = query.eq(key, value)
    response = query.execute()
    return int(response.count or 0)


@router.get("")
async def dashboard_overview(tenant: DashboardTenant) -> dict[str, Any]:
    """Aggregate counts for dashboard landing page."""
    tenant_id = tenant.tenant_id
    client = get_supabase_client()

    open_escalations = _count_rows("escalations", tenant_id=tenant_id, filters={"status": "open"})
    payment_resp = (
        client.table("escalations")
        .select("id", count="exact")
        .eq("tenant_id", tenant_id)
        .eq("status", "open")
        .in_("reason_code", [PAYMENT_RECEIPT, "enrollment_payment_review"])
        .execute()
    )
    tutor_resp = (
        client.table("escalations")
        .select("id", count="exact")
        .eq("tenant_id", tenant_id)
        .eq("status", "open")
        .eq("reason_code", TALK_TO_TUTOR)
        .execute()
    )
    pending_enrollments = _count_rows(
        "enrollments",
        tenant_id=tenant_id,
        filters={"status": "pending"},
    )
    students = _count_rows("students", tenant_id=tenant_id)
    classes = _count_rows("subject_classes", tenant_id=tenant_id)

    return {
        "tenant_id": tenant_id,
        "open_escalations": open_escalations,
        "open_payment_receipts": int(payment_resp.count or 0),
        "open_talk_to_tutor": int(tutor_resp.count or 0),
        "pending_enrollments": pending_enrollments,
        "students": students,
        "classes": classes,
    }
