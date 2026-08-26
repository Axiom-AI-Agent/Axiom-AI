"""FAQ intelligence endpoint for dashboard staff."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.tenant_scope import DashboardTenant
from services.faq_analysis_service import analyze_faqs

router = APIRouter(prefix="/faqs", tags=["dashboard-faqs"])


@router.post("/analyze")
async def analyze_tenant_faqs(
    tenant: DashboardTenant,
    limit: int = Query(200, ge=20, le=500),
    minimum_frequency: int = Query(2, ge=1, le=20),
) -> dict[str, Any]:
    """Cluster recent student questions into recurring FAQ themes."""
    try:
        return analyze_faqs(
            tenant_id=tenant.tenant_id,
            limit=limit,
            minimum_frequency=minimum_frequency,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"FAQ analysis failed: {exc}",
        ) from exc
