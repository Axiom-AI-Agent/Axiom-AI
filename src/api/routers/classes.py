"""Subject class listing — dashboard API."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Query

from services.admissions.admissions_db_client import AdmissionsDbClient

router = APIRouter(prefix="/classes", tags=["classes"])


@router.get("")
async def list_classes(
    tenant_id: str = Query(..., description="Tenant ID"),
    subject: Optional[str] = Query(None),
    grade: Optional[str] = Query(None),
) -> dict[str, Any]:
    """List available classes for a tenant."""
    db = AdmissionsDbClient()
    classes = db.list_classes(tenant_id=tenant_id, subject=subject, grade=grade)
    return {"tenant_id": tenant_id, "classes": classes}
