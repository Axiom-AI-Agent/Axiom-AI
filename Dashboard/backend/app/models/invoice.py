from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.models.enums import InvoiceStatus


class Invoice(Base):
    """
    Represents a student's invoice for a specific billing period.
    """

    __tablename__ = "invoices"
    __table_args__ = (
        Index("idx_invoices_tenant_status", "tenant_id", "status"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Keys
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    student_id = Column(
        String,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Invoice Details
    period = Column(
        String,
        nullable=False,
    )

    amount_due = Column(
        Numeric(12, 2),
        nullable=False,
    )

    status = Column(
        Enum(InvoiceStatus, name="invoice_status"),
        nullable=False,
        server_default="pending",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    tenant = relationship(
        "Tenant",
        back_populates="invoices",
    )

    student = relationship(
        "Student",
        back_populates="invoices",
    )

    bank_slip_uploads = relationship(
        "BankSlipUpload",
        back_populates="invoice",
    )

    def __repr__(self):
        return (
            f"<Invoice("
            f"id='{self.id}', "
            f"student='{self.student_id}', "
            f"period='{self.period}', "
            f"status='{self.status.value}')>"
        )