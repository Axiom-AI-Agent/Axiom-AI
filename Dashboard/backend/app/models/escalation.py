from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.models.enums import EscalationStatus


class Escalation(Base):
    """
    Represents a conversation that requires manual intervention
    from a staff member.
    """

    __tablename__ = "escalations"

    __table_args__ = (
        Index(
            "idx_escalations_tenant_status",
            "tenant_id",
            "status",
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

    student_id = Column(
        String,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Escalation Details
    reason_code = Column(
        String,
        nullable=False,
    )

    status = Column(
        Enum(EscalationStatus, name="escalation_status"),
        nullable=False,
        server_default="open",
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
        back_populates="escalations",
    )

    student = relationship(
        "Student",
        back_populates="escalations",
    )

    def __repr__(self):
        return (
            f"<Escalation("
            f"id='{self.id}', "
            f"student='{self.student_id}', "
            f"status='{self.status.value}')>"
        )