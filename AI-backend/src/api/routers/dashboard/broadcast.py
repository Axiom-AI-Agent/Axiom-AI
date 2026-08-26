"""Staff class broadcast to Telegram-linked students."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import (
    ClassBroadcastRecipientsResponse,
    ClassBroadcastRequest,
    ClassBroadcastResponse,
)
from api.tenant_scope import DashboardTenant, assert_body_tenant
from services.messaging.class_broadcast import (
    ClassNotFoundError,
    resolve_broadcast_audience,
    send_class_broadcast,
)

router = APIRouter(prefix="/classes", tags=["dashboard-broadcast"])


@router.get("/{class_id}/broadcast-recipients", response_model=ClassBroadcastRecipientsResponse)
async def get_broadcast_recipients(
    class_id: str,
    tenant: DashboardTenant,
) -> ClassBroadcastRecipientsResponse:
    """Preview who would receive a Telegram class announcement."""
    try:
        audience = resolve_broadcast_audience(
            tenant_id=tenant.tenant_id,
            class_id=class_id,
        )
    except ClassNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Class not found") from exc

    return ClassBroadcastRecipientsResponse(
        class_id=audience.class_id,
        class_name=audience.class_name,
        enrolled=audience.enrolled,
        reachable=len(audience.reachable),
        skipped_no_telegram=audience.skipped_no_telegram,
        reachable_names=audience.reachable_names,
    )


@router.post("/{class_id}/broadcast", response_model=ClassBroadcastResponse)
async def post_class_broadcast(
    class_id: str,
    body: ClassBroadcastRequest,
    tenant: DashboardTenant,
) -> ClassBroadcastResponse:
    """Send a class announcement to Telegram-linked enrolled students."""
    assert_body_tenant(body.tenant_id, tenant)
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        result = await send_class_broadcast(
            tenant_id=tenant.tenant_id,
            class_id=class_id,
            message=message,
        )
    except ClassNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Class not found") from exc

    return ClassBroadcastResponse(
        class_id=class_id,
        sent=result.sent,
        failed=result.failed,
        skipped_no_telegram=result.skipped_no_telegram,
        failures=[
            {"student_id": failure.student_id, "name": failure.name}
            for failure in result.failures
        ],
    )
