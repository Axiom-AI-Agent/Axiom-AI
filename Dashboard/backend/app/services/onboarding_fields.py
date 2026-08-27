"""Persist and lock per-tenant onboarding field definitions."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import Tenant, TenantFieldDefinition
from app.schemas.auth import OnboardingFieldInput


class FieldConfigLockedError(ValueError):
    """Raised when staff try to change fields after setup is locked."""


def save_tenant_onboarding_fields(
    db: Session,
    tenant: Tenant,
    fields: list[OnboardingFieldInput],
    *,
    lock: bool = True,
) -> None:
    if bool(tenant.field_config_locked):
        raise FieldConfigLockedError(
            "Onboarding fields are locked and cannot be changed."
        )

    (
        db.query(TenantFieldDefinition)
        .filter(TenantFieldDefinition.tenant_id == tenant.id)
        .delete()
    )

    for index, item in enumerate(fields):
        db.add(
            TenantFieldDefinition(
                id=str(uuid.uuid4()),
                tenant_id=tenant.id,
                field_key=item.field_key,
                label=item.label,
                field_type=item.field_type,
                options=item.options,
                required=item.required,
                sort_order=index,
                active=True,
            )
        )

    if lock:
        tenant.field_config_locked = True
