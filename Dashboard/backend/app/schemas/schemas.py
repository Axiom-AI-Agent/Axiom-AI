import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ChatChannel, EscalationStatus, EnrollmentStatus

# Hardcoded for hackathon demo — matches sql/02_seed_demo.sql
DEMO_TENANT_ID = "tenant-demo-physics"


# ---------- Classes ----------
class ClassBase(BaseModel):
    subject: str
    fee_amount: Decimal
    fee_cycle: str = "monthly"
    name: Optional[str] = None
    grade: Optional[str] = None


class ClassCreate(ClassBase):
    tenant_id: str = DEMO_TENANT_ID


class ClassUpdate(BaseModel):
    subject: Optional[str] = None
    fee_amount: Optional[Decimal] = None
    fee_cycle: Optional[str] = None
    name: Optional[str] = None
    grade: Optional[str] = None


class ClassResponse(ClassBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Enrollments ----------
class EnrollmentSummary(BaseModel):
    id: str
    class_id: str
    class_subject: Optional[str] = None
    class_name: Optional[str] = None
    status: EnrollmentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentCreate(BaseModel):
    class_id: str
    status: EnrollmentStatus = EnrollmentStatus.PENDING


# ---------- Students ----------
class StudentBase(BaseModel):
    name: Optional[str] = None
    phone: str
    school: Optional[str] = None
    district: Optional[str] = None
    language_pref: str = "en"
    extra_fields: dict[str, Any] = Field(default_factory=dict)

    @field_validator("extra_fields", mode="before")
    @classmethod
    def default_extra_fields(cls, value: Any) -> dict[str, Any]:
        return value or {}


class StudentCreate(StudentBase):
    tenant_id: str = DEMO_TENANT_ID
    class_id: Optional[str] = Field(
        default=None,
        description="Optional class to enroll the student in on creation",
    )


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    school: Optional[str] = None
    district: Optional[str] = None
    language_pref: Optional[str] = None
    extra_fields: Optional[dict[str, Any]] = None


class StudentResponse(StudentBase):
    id: str
    tenant_id: str
    human_mode: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True



class StudentDetailResponse(StudentResponse):
    enrollments: list[EnrollmentSummary] = Field(default_factory=list)


class StudentsListResponse(BaseModel):
    tenant_id: str
    students: list[StudentDetailResponse]

class StudentHumanModeUpdate(BaseModel):
    human_mode: bool
# ---------- Escalations ----------
class EscalationCreate(BaseModel):
    tenant_id: str = DEMO_TENANT_ID
    student_id: str
    reason_code: str
    enrollment_id: Optional[str] = None
    media_url: Optional[str] = None
    student_message: Optional[str] = None


class EscalationResponse(BaseModel):
    id: str
    tenant_id: str
    student_id: str
    student_name: Optional[str] = None
    student_phone: Optional[str] = None
    enrollment_id: Optional[str] = None
    reason_code: str
    status: EscalationStatus
    student_message: Optional[str] = None
    media_url: Optional[str] = None
    resolution: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EscalationsListResponse(BaseModel):
    tenant_id: str
    escalations: list[EscalationResponse]


class EscalationActionResponse(BaseModel):
    ok: bool
    escalation_id: str
    reason_code: str
    resolution: Optional[str] = None
    enrollment_status: Optional[str] = None
    student_notified: bool = False
    notification_message: Optional[str] = None


# ---------- Dashboard overview ----------
class DashboardOverviewResponse(BaseModel):
    tenant_id: str
    open_escalations: int
    open_payment_receipts: int
    open_talk_to_tutor: int
    pending_enrollments: int
    students: int
    classes: int

class EscalationCategoryMetric(BaseModel):
    reason_code: str
    count: int


class StudentAnalyticsMetric(BaseModel):
    student_id: str
    student_name: Optional[str] = None
    messages: int
    conversations: int
    escalations: int


class DashboardAnalyticsResponse(BaseModel):
    tenant_id: str

    total_conversations: int
    total_messages: int

    deflected_conversations: int
    deflection_rate: float

    average_response_seconds: float
    estimated_minutes_saved: int

    total_escalations: int
    open_escalations: int
    resolved_escalations: int

    escalation_categories: list[EscalationCategoryMetric]
    students: list[StudentAnalyticsMetric]
    
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


class InvoiceCreate(BaseModel):
    tenant_id: str = DEMO_TENANT_ID
    student_id: str
    period: str
    amount_due: Decimal


# ---------- Message Logs ----------
class MessageLogCreate(BaseModel):
    tenant_id: str = DEMO_TENANT_ID
    student_id: str
    channel: ChatChannel = ChatChannel.TWILIO_WHATSAPP
    intent: Optional[str] = None


class MessageLogResponse(BaseModel):
    id: str
    tenant_id: str
    student_id: str
    student_name: Optional[str] = None
    channel: ChatChannel
    intent: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# ---------- Tenant / Settings ----------
class TenantSummary(BaseModel):
    id: str
    name: str
    slug: str
    status: str

    class Config:
        from_attributes = True


class TenantsListResponse(BaseModel):
    tenants: list[TenantSummary]


class TenantProfileResponse(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    whatsapp_number: Optional[str] = None
    drive_folder_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    payments_enabled: bool = True
    field_config_locked: bool = False

    class Config:
        from_attributes = True


class TenantUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str = Field(min_length=1, max_length=100)
    whatsapp_number: Optional[str] = None
    drive_folder_id: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(active|suspended)$")
    payments_enabled: Optional[bool] = None
class ClassAnalyticsMetric(BaseModel):
    class_id: str
    class_name: Optional[str] = None
    subject: str
    grade: Optional[str] = None

    enrolled_students: int
    active_students: int
    pending_students: int

    total_messages: int
    total_conversations: int

    deflected_conversations: int
    deflection_rate: float

    average_response_seconds: float
    estimated_minutes_saved: int

    total_escalations: int
    open_escalations: int
    resolved_escalations: int


class ClassAnalyticsComparisonResponse(BaseModel):
    tenant_id: str
    attribution_mode: str
    classes: list[ClassAnalyticsMetric]