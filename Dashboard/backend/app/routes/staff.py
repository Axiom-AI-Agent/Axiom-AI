import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import StaffUser
from app.models.enums import StaffRole
from app.schemas.auth import StaffCreate, StaffResponse, StaffUpdate
from app.services.auth_service import hash_password

router = APIRouter(prefix="/staff", tags=["Staff"])


def _to_response(staff: StaffUser) -> dict:
    return {
        "id": staff.id,
        "tenant_id": staff.tenant_id,
        "name": staff.name,
        "email": staff.email,
        "role": staff.role.value,
        "is_active": staff.is_active,
    }


@router.get("", response_model=list[StaffResponse])
def list_staff(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(StaffUser)
        .filter(StaffUser.tenant_id == tenant_id)
        .order_by(StaffUser.name.asc())
        .all()
    )
    return [_to_response(row) for row in rows]


@router.post("", response_model=StaffResponse, status_code=201)
def create_staff(
    payload: StaffCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    staff = StaffUser(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name=payload.name.strip(),
        email=str(payload.email).strip().lower(),
        password_hash=hash_password(payload.password),
        role=StaffRole(payload.role),
        is_active=True,
    )

    try:
        db.add(staff)
        db.commit()
        db.refresh(staff)
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A staff member with this email already exists.",
        ) from error

    return _to_response(staff)


@router.patch("/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: str,
    payload: StaffUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    staff = (
        db.query(StaffUser)
        .filter(
            StaffUser.id == staff_id,
            StaffUser.tenant_id == tenant_id,
        )
        .first()
    )

    if staff is None:
        raise HTTPException(status_code=404, detail="Staff member not found")

    if payload.name is not None:
        staff.name = payload.name.strip()  # type: ignore[assignment]
    if payload.role is not None:
        staff.role = StaffRole(payload.role)  # type: ignore[assignment]
    if payload.is_active is not None:
        staff.is_active = payload.is_active  # type: ignore[assignment]

    db.commit()
    db.refresh(staff)
    return _to_response(staff)
