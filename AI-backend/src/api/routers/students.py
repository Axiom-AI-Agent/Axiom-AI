"""Student registration and lookup — dashboard + dev API."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from agents.tools.crm_tool import CrmTool
from services.admissions.admissions_db_client import AdmissionsDbClient

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/register")
async def register_student(
    tenant_id: str = Query(..., description="Tenant ID"),
    phone: str = Query(..., description="Student phone (digits)"),
    name: Optional[str] = Query(None),
    school: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    consent: bool = Query(False, description="PDPA consent flag"),
) -> dict[str, Any]:
    """Register or update a student profile (dashboard / manual onboarding)."""
    tool = CrmTool()
    raw = tool.register_student(
        tenant_id=tenant_id,
        phone=phone,
        name=name,
        school=school,
        district=district,
        consent=consent,
    )
    import json

    payload = json.loads(raw)
    if not payload.get("ok"):
        raise HTTPException(status_code=400, detail=payload.get("error", "Registration failed"))
    return payload["student"]


@router.get("/{phone}")
async def get_student(
    phone: str,
    tenant_id: str = Query(..., description="Tenant ID"),
) -> dict[str, Any]:
    """Fetch student profile and enrollments by phone."""
    db = AdmissionsDbClient()
    student = db.get_student(tenant_id=tenant_id, phone=phone)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    enrollments = db.list_enrollments(tenant_id=tenant_id, student_id=student["id"])
    return {"student": student, "enrollments": enrollments}
