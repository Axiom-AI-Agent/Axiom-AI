"""Tenant scope for dashboard API requests."""

from fastapi import Header, HTTPException, Query

from app.schemas.schemas import DEMO_TENANT_ID


def get_tenant_id(
    tenant_id: str | None = Query(None, alias="tenant_id"),
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
) -> str:
    query_tenant = tenant_id
    header_tenant = x_tenant_id

    if query_tenant and header_tenant and query_tenant != header_tenant:
        raise HTTPException(status_code=400, detail="tenant_id mismatch")

    return query_tenant or header_tenant or DEMO_TENANT_ID
