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
from app.models.enums import FeeCycle


class SubjectClass(Base):
    """
    Represents a tuition class offered by a tenant.
    """

    __tablename__ = "subject_classes"
    __table_args__ = (
        Index("idx_subject_classes_tenant", "tenant_id"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Key
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Class Details
    subject = Column(
        String,
        nullable=False,
    )

    name = Column(String, nullable=True)
    grade = Column(String, nullable=True)

    fee_amount = Column(
        Numeric(12, 2),
        nullable=False,
        server_default="0",
    )

    fee_cycle = Column(
        Enum(FeeCycle, name="fee_cycle", values_callable=lambda enum: [e.value for e in enum]),
        nullable=False,
        server_default="monthly",
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
        back_populates="subject_classes",
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="subject_class",
    )

    def __repr__(self):
        return (
            f"<SubjectClass("
            f"id='{self.id}', "
            f"subject='{self.subject}')>"
        )