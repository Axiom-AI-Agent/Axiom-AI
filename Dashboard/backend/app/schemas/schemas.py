import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

# Hardcoded for hackathon demo — matches sql/02_seed_demo.sql
DEMO_TENANT_ID = "tenant-demo-physics"


# ---------- Classes ----------
class ClassBase(BaseModel):
    subject: str
    fee_amount: Decimal
    fee_cycle: str = "monthly"


class ClassCreate(ClassBase):
    tenant_id: str = DEMO_TENANT_ID


class ClassResponse(ClassBase):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Invoices / Payments ----------
class InvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    student_id: str
    period: str
    amount_due: Decimal
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentApproveReject(BaseModel):
    reason: Optional[str] = None


# ---------- Students ----------
class StudentBase(BaseModel):
    name: Optional[str] = None
    phone: str
    district: Optional[str] = None
    language_pref: str = "en"


class StudentCreate(StudentBase):
    tenant_id: str = DEMO_TENANT_ID


class StudentResponse(StudentBase):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Escalations ----------
class EscalationResponse(BaseModel):
    id: str
    tenant_id: str
    student_id: str
    reason_code: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Invoices ----------
class InvoiceCreate(BaseModel):
    tenant_id: str = DEMO_TENANT_ID
    student_id: str
    period: str
    amount_due: Decimal