"""Domain status enums — mirror PostgreSQL ENUM types in sql/01_schema.sql."""

from enum import Enum


class TenantStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


class EnrollmentStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    WITHDRAWN = "withdrawn"


class InvoiceStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    DISPUTED = "disputed"


class PaymentStatus(str, Enum):
    """Bank-slip review workflow — kept for dashboard API compatibility."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class EscalationStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    RESOLVED = "resolved"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatChannel(str, Enum):
    HTTP_DEV = "http_dev"
    TWILIO_WHATSAPP = "twilio_whatsapp"
    TELEGRAM = "telegram"


class StaffRole(str, Enum):
    ADMIN = "admin"
    MARKER = "marker"
    VIEWER = "viewer"


class FeeCycle(str, Enum):
    MONTHLY = "monthly"
    TERMLY = "termly"
    ANNUAL = "annual"
