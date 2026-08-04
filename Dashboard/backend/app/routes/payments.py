from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Payment

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/pending")
def get_pending_payments(db: Session = Depends(get_db)):
    return db.query(Payment).filter(getattr(Payment, "status") == "PENDING").all()

@router.put("/{payment_id}/approve")
def approve_payment(payment_id: int, db: Session = Depends(get_db)):
    payment: Payment | None = db.query(Payment).filter(getattr(Payment, "id") == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    setattr(payment, "status", "APPROVED")
    db.commit()
    return {"message": "Payment approved successfully"}

@router.put("/{payment_id}/reject")
def reject_payment(payment_id: int, db: Session = Depends(get_db)):
    payment: Payment | None = db.query(Payment).filter(getattr(Payment, "id") == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    setattr(payment, "status", "REJECTED")
    db.commit()
    return {"message": "Payment rejected successfully"}