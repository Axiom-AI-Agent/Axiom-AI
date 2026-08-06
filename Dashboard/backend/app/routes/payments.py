from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Invoice
from app.models.enums import InvoiceStatus
from app.schemas.schemas import InvoiceResponse

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/pending", response_model=list[InvoiceResponse])
def get_pending_payments(db: Session = Depends(get_db)):
    return (
        db.query(Invoice)
        .filter(Invoice.status == InvoiceStatus.PENDING)
        .all()
    )


@router.put("/{invoice_id}/approve", response_model=InvoiceResponse)
def approve_payment(invoice_id: str, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = InvoiceStatus.PAID # type: ignore
    db.commit()
    db.refresh(invoice)
    return invoice


@router.put("/{invoice_id}/reject", response_model=InvoiceResponse)
def reject_payment(invoice_id: str, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = InvoiceStatus.DISPUTED # type: ignore
    db.commit()
    db.refresh(invoice)
    return invoice