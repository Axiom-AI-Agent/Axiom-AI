"""Domain enum tests."""

import pytest
from pydantic import ValidationError

from api.schemas import PaymentStatusUpdate, TenantSummary
from domain.enums import (
    ChatChannel,
    EnrollmentStatus,
    EscalationStatus,
    FeeCycle,
    InvoiceStatus,
    MessageRole,
    PaymentStatus,
    StaffRole,
    TenantStatus,
)


@pytest.mark.parametrize(
    ("enum_cls", "member", "value"),
    [
        (TenantStatus, TenantStatus.ACTIVE, "active"),
        (EnrollmentStatus, EnrollmentStatus.PAUSED, "paused"),
        (InvoiceStatus, InvoiceStatus.OVERDUE, "overdue"),
        (PaymentStatus, PaymentStatus.PENDING, "pending"),
        (EscalationStatus, EscalationStatus.OPEN, "open"),
        (MessageRole, MessageRole.ASSISTANT, "assistant"),
        (ChatChannel, ChatChannel.TWILIO_WHATSAPP, "twilio_whatsapp"),
        (ChatChannel, ChatChannel.TELEGRAM, "telegram"),
        (StaffRole, StaffRole.MARKER, "marker"),
        (FeeCycle, FeeCycle.TERMLY, "termly"),
    ],
)
def test_enum_values(enum_cls, member, value):
    assert member == value
    assert enum_cls(value) is member


def test_payment_status_update_accepts_enum():
    body = PaymentStatusUpdate(status=PaymentStatus.APPROVED)
    assert body.status is PaymentStatus.APPROVED


def test_payment_status_update_rejects_invalid():
    with pytest.raises(ValidationError):
        PaymentStatusUpdate(status="maybe")


def test_tenant_summary_schema():
    row = TenantSummary(id="tenant-demo-physics", slug="demo-physics", status=TenantStatus.ACTIVE)
    assert row.status.value == "active"
