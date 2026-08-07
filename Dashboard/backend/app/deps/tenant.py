"""Authenticated tenant scope for dashboard API requests."""

from fastapi import (
    Depends,
    Header,
    HTTPException,
    Query,
)

from app.deps.auth import (
    get_current_staff,
)

from app.models import StaffUser


def get_tenant_id(
    tenant_id: str | None = Query(
        None,
        alias="tenant_id",
    ),
    x_tenant_id: str | None = Header(
        None,
        alias="X-Tenant-ID",
    ),
    current_staff: StaffUser = Depends(
        get_current_staff,
    ),
) -> str:

    authenticated_tenant = (
        current_staff.tenant_id
    )

    supplied_tenant = (
        tenant_id
        or x_tenant_id
    )

    if (
        tenant_id
        and x_tenant_id
        and tenant_id
        != x_tenant_id
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "tenant_id mismatch"
            ),
        )

    if (
        supplied_tenant
        and supplied_tenant
        != authenticated_tenant
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot access another tenant."
            ),
        )

    return authenticated_tenant