from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.enums import InvoiceStatus, EscalationStatus
from app.models import Student, Invoice, Escalation, MessageLog

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return {
        "total_students": db.query(Student).count(),
        "pending_payments": db.query(Invoice).filter(Invoice.status == InvoiceStatus.PENDING).count(),
        "open_escalations": db.query(Escalation).filter(Escalation.status == EscalationStatus.OPEN).count(),
    }

@router.get("/payments")
def get_dashboard_payments(db: Session = Depends(get_db)):
    return (
        db.query(Invoice)
        .order_by(Invoice.created_at.desc())
        .all()
    )

@router.get("/escalations")
def get_dashboard_escalations(db: Session = Depends(get_db)):
    return (
        db.query(Escalation)
        .order_by(Escalation.created_at.desc())
        .all()
    )

@router.get("/chat-logs")
def get_dashboard_chat_logs(db: Session = Depends(get_db)):
    return (
        db.query(MessageLog)
        .order_by(MessageLog.timestamp.desc())
        .all()
    )