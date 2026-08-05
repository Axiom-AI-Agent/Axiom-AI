from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Float,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class BankSlipUpload(Base):
    """
    Represents a bank slip uploaded by a student for invoice verification.
    """

    __tablename__ = "bank_slip_uploads"

    __table_args__ = (
        Index(
            "idx_bank_slip_uploads_invoice",
            "invoice_id",
        ),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Keys
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    invoice_id = Column(
        String,
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Upload Details
    image_ref = Column(
        String,
        nullable=False,
    )

    confidence_score = Column(
        Float,
        nullable=True,
    )

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    tenant = relationship(
        "Tenant",
        back_populates="bank_slip_uploads",
    )

    invoice = relationship(
        "Invoice",
        back_populates="bank_slip_uploads",
    )

    def __repr__(self):
        return (
            f"<BankSlipUpload("
            f"id='{self.id}', "
            f"invoice='{self.invoice_id}')>"
        )