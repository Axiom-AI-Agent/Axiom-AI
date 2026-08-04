import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import SubjectClass
from app.schemas.schemas import ClassCreate, ClassResponse

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=List[ClassResponse])
def get_classes(db: Session = Depends(get_db)):
    return db.query(SubjectClass).all()


@router.post("", response_model=ClassResponse)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    new_class = SubjectClass(
        id=str(uuid.uuid4()),
        tenant_id=class_data.tenant_id,
        subject=class_data.subject,
        fee_amount=class_data.fee_amount,
        fee_cycle=class_data.fee_cycle,
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class