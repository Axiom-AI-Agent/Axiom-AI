from sqlalchemy import Boolean, Column, DateTime, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.models.enums import TenantStatus


class Tenant(Base):
    """
    Represents a tuition institute (tenant) in the Axiom AI platform.
    Every business entity belongs to a tenant.
    """

    __tablename__ = "tenants"

    # Primary Key
    id = Column(String, primary_key=True)

    # Basic Information
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)

    # Status
    status = Column(
        Enum(TenantStatus, name="tenant_status", values_callable=lambda enum: [e.value for e in enum]),
        nullable=False,
        server_default="active",
    )

    # Configuration
    whatsapp_number = Column(String, nullable=True)
    drive_folder_id = Column(String, nullable=True)
    payments_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    telegram_bot_username = Column(String, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    staff_users = relationship("StaffUser", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")

    parent_guardians = relationship("ParentGuardian", back_populates="tenant")
    students = relationship("Student", back_populates="tenant")

    subject_classes = relationship("SubjectClass", back_populates="tenant")
    enrollments = relationship("Enrollment", back_populates="tenant")

    invoices = relationship("Invoice", back_populates="tenant")
    bank_slip_uploads = relationship("BankSlipUpload", back_populates="tenant")

    message_logs = relationship("MessageLog", back_populates="tenant")
    escalations = relationship("Escalation", back_populates="tenant")

    # Memory relationships
    mem_procedures = relationship("MemProcedure", back_populates="tenant")
    mem_facts = relationship("MemFact", back_populates="tenant")
    mem_episodes = relationship("MemEpisode", back_populates="tenant")
    st_turns = relationship("STTurn", back_populates="tenant")

    def __repr__(self):
        return f"<Tenant(id='{self.id}', name='{self.name}')>"