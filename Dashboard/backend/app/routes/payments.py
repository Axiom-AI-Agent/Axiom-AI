from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import Invoice
from app.models.enums import InvoiceStatus
from app.schemas.schemas import InvoiceResponse


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.get(
    "/pending",
    response_model=list[InvoiceResponse],
)
def get_pending_payments(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    return (
        db.query(Invoice)
        .filter(
            Invoice.tenant_id == tenant_id,
            Invoice.status == InvoiceStatus.PENDING,
        )
        .order_by(Invoice.created_at.desc())
        .all()
    )


@router.put(
    "/{invoice_id}/approve",
    response_model=InvoiceResponse,
)
def approve_payment(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant_id,
        )
        .first()
    )

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    invoice.status = InvoiceStatus.PAID  # type: ignore

    db.commit()
    db.refresh(invoice)

    return invoice


@router.put(
    "/{invoice_id}/reject",
    response_model=InvoiceResponse,
)
def reject_payment(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    invoice = (
        db.query(Invoice)
        .filter(
            Invoice.id == invoice_id,
            Invoice.tenant_id == tenant_id,
        )
        .first()
    )

    if invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )

    invoice.status = InvoiceStatus.DISPUTED  # type: ignore

    db.commit()
    db.refresh(invoice)

    return invoice