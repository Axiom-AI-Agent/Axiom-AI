from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Student, Invoice, Escalation
from app.models.enums import InvoiceStatus, EscalationStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return {
        "total_students": db.query(Student).count(),
        "pending_payments": db.query(Invoice).filter(Invoice.status == InvoiceStatus.PENDING).count(),
        "open_escalations": db.query(Escalation).filter(Escalation.status == EscalationStatus.OPEN).count(),
    }