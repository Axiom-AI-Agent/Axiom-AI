import uuid
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Invoice
from app.models.enums import InvoiceStatus
from app.schemas.schemas import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("", response_model=List[InvoiceResponse])
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).order_by(Invoice.created_at.desc()).all()


@router.post("", response_model=InvoiceResponse)
def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db)):
    new_invoice = Invoice(
        id=str(uuid.uuid4()),
        tenant_id=invoice_data.tenant_id,
        student_id=invoice_data.student_id,
        period=invoice_data.period,
        amount_due=invoice_data.amount_due,
        status=InvoiceStatus.PENDING,
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice