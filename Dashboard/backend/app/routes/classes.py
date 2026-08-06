import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import SubjectClass
from app.models.enums import FeeCycle
from app.schemas.schemas import ClassCreate, ClassResponse, ClassUpdate

router = APIRouter(prefix="/classes", tags=["Classes"])


def _parse_fee_cycle(value: str) -> FeeCycle:
    normalized = value.lower().replace("-", "_")
    mapping = {
        "monthly": FeeCycle.MONTHLY,
        "termly": FeeCycle.TERMLY,
        "annual": FeeCycle.ANNUAL,
        "one_time": FeeCycle.ANNUAL,
    }

    if normalized not in mapping:
        raise HTTPException(status_code=422, detail=f"Invalid fee_cycle: {value}")

    return mapping[normalized]


@router.get("", response_model=List[ClassResponse])
def get_classes(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return (
        db.query(SubjectClass)
        .filter(SubjectClass.tenant_id == tenant_id)
        .order_by(SubjectClass.created_at.desc())
        .all()
    )


@router.get("/{class_id}", response_model=ClassResponse)
def get_class(
    class_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    subject_class = (
        db.query(SubjectClass)
        .filter(
            SubjectClass.id == class_id,
            SubjectClass.tenant_id == tenant_id,
        )
        .first()
    )

    if subject_class is None:
        raise HTTPException(status_code=404, detail="Class not found")

    return subject_class


@router.post("", response_model=ClassResponse, status_code=201)
def create_class(
    class_data: ClassCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    if class_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="tenant_id mismatch")

    new_class = SubjectClass(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        subject=class_data.subject.strip(),
        name=class_data.name,
        grade=class_data.grade,
        fee_amount=class_data.fee_amount,
        fee_cycle=_parse_fee_cycle(class_data.fee_cycle),
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


@router.put("/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: str,
    class_data: ClassUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    subject_class = (
        db.query(SubjectClass)
        .filter(
            SubjectClass.id == class_id,
            SubjectClass.tenant_id == tenant_id,
        )
        .first()
    )

    if subject_class is None:
        raise HTTPException(status_code=404, detail="Class not found")

    if class_data.subject is not None:
        subject_class.subject = class_data.subject.strip()  # type: ignore[assignment]
    if class_data.name is not None:
        subject_class.name = class_data.name  # type: ignore[assignment]
    if class_data.grade is not None:
        subject_class.grade = class_data.grade  # type: ignore[assignment]
    if class_data.fee_amount is not None:
        subject_class.fee_amount = class_data.fee_amount  # type: ignore[assignment]
    if class_data.fee_cycle is not None:
        subject_class.fee_cycle = _parse_fee_cycle(class_data.fee_cycle)  # type: ignore[assignment]

    db.commit()
    db.refresh(subject_class)
    return subject_class


@router.delete("/{class_id}", status_code=204)
def delete_class(
    class_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    subject_class = (
        db.query(SubjectClass)
        .filter(
            SubjectClass.id == class_id,
            SubjectClass.tenant_id == tenant_id,
        )
        .first()
    )

    if subject_class is None:
        raise HTTPException(status_code=404, detail="Class not found")

    db.delete(subject_class)
    db.commit()
