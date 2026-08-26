"""Tenant scope validation for staff / dashboard endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query

from domain.enums import TenantStatus
from infrastructure.db.supabase_client import get_supabase_client


@dataclass(frozen=True)
class TenantScope:
    """Resolved, active tenant — all dashboard queries must use this scope."""

    tenant_id: str
    slug: str | None = None
    name: str | None = None


def resolve_tenant_id(
    tenant_id: str | None = Query(
        None,
        description="Tenant ID (required unless X-Tenant-ID header is set)",
    ),
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
) -> str:
    """
    Resolve tenant from query param or X-Tenant-ID header.

    Dashboard frontend should send X-Tenant-ID from the authenticated staff
    session; query param remains supported for curl and local dev.
    """
    query_tid = (tenant_id or "").strip()
    header_tid = (x_tenant_id or "").strip()
    if query_tid and header_tid and query_tid != header_tid:
        raise HTTPException(
            status_code=400,
            detail="tenant_id query param conflicts with X-Tenant-ID header",
        )
    resolved = header_tid or query_tid
    if not resolved:
        raise HTTPException(
            status_code=400,
            detail="tenant_id is required (query param or X-Tenant-ID header)",
        )
    return resolved


def require_active_tenant(
    tenant_id: Annotated[str, Depends(resolve_tenant_id)],
) -> TenantScope:
    """Ensure the tenant exists and is active before any dashboard handler runs."""
    client = get_supabase_client()
    response = (
        client.table("tenants")
        .select("id, slug, name, status")
        .eq("id", tenant_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    if not rows:
        raise HTTPException(status_code=404, detail=f"Unknown tenant: {tenant_id}")
    row = rows[0]
    if row.get("status") != TenantStatus.ACTIVE.value:
        raise HTTPException(status_code=403, detail=f"Tenant is not active: {tenant_id}")
    return TenantScope(
        tenant_id=str(row["id"]),
        slug=row.get("slug"),
        name=row.get("name"),
    )


def assert_body_tenant(body_tenant_id: str, tenant: TenantScope) -> None:
    """Reject POST bodies whose tenant_id does not match the resolved scope."""
    if body_tenant_id.strip() != tenant.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Request body tenant_id does not match tenant scope",
        )


def assert_session_for_tenant(session_id: str, tenant: TenantScope) -> None:
    """Defense-in-depth: session ids are `{tenant_id}:{phone}`."""
    prefix = f"{tenant.tenant_id}:"
    if not session_id.startswith(prefix):
        raise HTTPException(
            status_code=403,
            detail="Session does not belong to this tenant",
        )


def assert_form_tenant(form_tenant_id: str, tenant: TenantScope) -> None:
    """Reject multipart/form uploads whose tenant_id does not match the resolved scope."""
    if form_tenant_id.strip() != tenant.tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Form tenant_id does not match tenant scope",
        )


DashboardTenant = Annotated[TenantScope, Depends(require_active_tenant)]
