import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import Tenant, TenantFieldDefinition
from app.models.enums import TenantStatus
from app.schemas.auth import (
    OnboardingFieldResponse,
    OnboardingFieldsPutRequest,
    OnboardingFieldsResponse,
)
from app.schemas.schemas import (
    TenantProfileResponse,
    TenantUpdate,
    TenantsListResponse,
)
from app.services.onboarding_fields import (
    FieldConfigLockedError,
    save_tenant_onboarding_fields,
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
    if (
        payload.payments_enabled
        is not None
    ):
        tenant.payments_enabled = (
            payload.payments_enabled
        )
    db.commit()
    db.refresh(tenant)

    return tenant


@router.get(
    "/tenant/onboarding-fields",
    response_model=OnboardingFieldsResponse,
)
def get_onboarding_fields(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    rows = (
        db.query(TenantFieldDefinition)
        .filter(TenantFieldDefinition.tenant_id == tenant_id)
        .order_by(TenantFieldDefinition.sort_order, TenantFieldDefinition.field_key)
        .all()
    )
    return OnboardingFieldsResponse(
        locked=bool(tenant.field_config_locked),
        fields=[
            OnboardingFieldResponse(
                field_key=row.field_key,
                label=row.label,
                field_type=row.field_type,
                options=list(row.options) if row.options else None,
                required=bool(row.required),
                sort_order=int(row.sort_order or 0),
                active=bool(row.active),
            )
            for row in rows
        ],
    )


@router.put(
    "/tenant/onboarding-fields",
    response_model=OnboardingFieldsResponse,
)
def replace_onboarding_fields(
    payload: OnboardingFieldsPutRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        save_tenant_onboarding_fields(
            db,
            tenant,
            payload.fields,
            lock=True,
        )
    except FieldConfigLockedError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    db.commit()
    db.refresh(tenant)
    return get_onboarding_fields(tenant_id=tenant_id, db=db)
