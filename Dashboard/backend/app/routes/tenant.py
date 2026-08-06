import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import Tenant
from app.models.enums import TenantStatus
from app.schemas.schemas import (
    TenantProfileResponse,
    TenantUpdate,
    TenantsListResponse,
)

router = APIRouter(tags=["Tenant Settings"])

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _normalize_slug(slug: str) -> str:
    return slug.strip().lower()


@router.get("/tenants", response_model=TenantsListResponse)
def list_tenants(db: Session = Depends(get_db)):
    tenants = db.query(Tenant).order_by(Tenant.name.asc()).all()
    return {"tenants": tenants}


@router.get("/tenant", response_model=TenantProfileResponse)
def get_tenant_profile(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


@router.put("/tenant", response_model=TenantProfileResponse)
def update_tenant_profile(
    payload: TenantUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()

    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    slug = _normalize_slug(payload.slug)

    if not SLUG_PATTERN.match(slug):
        raise HTTPException(
            status_code=422,
            detail="Slug must be lowercase letters, numbers, and hyphens only",
        )

    conflict = (
        db.query(Tenant)
        .filter(Tenant.slug == slug, Tenant.id != tenant_id)
        .first()
    )

    if conflict is not None:
        raise HTTPException(status_code=409, detail="Slug is already in use")

    tenant.name = payload.name.strip()  # type: ignore[assignment]
    tenant.slug = slug  # type: ignore[assignment]
    tenant.whatsapp_number = payload.whatsapp_number  # type: ignore[assignment]
    tenant.drive_folder_id = payload.drive_folder_id  # type: ignore[assignment]

    if payload.status is not None:
        tenant.status = TenantStatus(payload.status)  # type: ignore[assignment]

    db.commit()
    db.refresh(tenant)

    return tenant
