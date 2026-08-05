from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Escalation
from app.models.enums import EscalationStatus
from app.schemas.schemas import (
    EscalationCreate,
    EscalationResponse,
)
from app.services.escalation_service import create_escalation

router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.get("", response_model=List[EscalationResponse])
def get_escalations(db: Session = Depends(get_db)):
    return db.query(Escalation).order_by(Escalation.created_at.desc()).all()


@router.get("/open", response_model=List[EscalationResponse])
def get_open_escalations(db: Session = Depends(get_db)):
    return db.query(Escalation).filter(Escalation.status == EscalationStatus.OPEN).all()

@router.post("", response_model=EscalationResponse)
def create_new_escalation(
    escalation_data: EscalationCreate,
    db: Session = Depends(get_db),
):
    return create_escalation(
        db=db,
        tenant_id=escalation_data.tenant_id,
        student_id=escalation_data.student_id,
        reason_code=escalation_data.reason_code,
    )