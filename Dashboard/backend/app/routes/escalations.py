from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Escalation
from app.schemas.schemas import EscalationResponse

router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.get("", response_model=List[EscalationResponse])
def get_escalations(db: Session = Depends(get_db)):
    return db.query(Escalation).order_by(Escalation.created_at.desc()).all()


@router.get("/open", response_model=List[EscalationResponse])
def get_open_escalations(db: Session = Depends(get_db)):
    return db.query(Escalation).filter(Escalation.status == "open").all()