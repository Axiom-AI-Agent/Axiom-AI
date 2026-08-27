from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression, func

from app.database.session import Base


class Student(Base):
    """
    Represents a student registered under a tenant.
    """

    __tablename__ = "students"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "phone",
            name="uq_students_tenant_phone",
        ),
        Index("idx_students_tenant_phone", "tenant_id", "phone"),
        Index("idx_students_parent", "parent_id"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Keys
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    parent_id = Column(
        String,
        ForeignKey("parent_guardians.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Student Details
    name = Column(
        String,
        nullable=True,
    )

    phone = Column(
        String,
        nullable=False,
    )

    school = Column(
        String,
        nullable=True,
    )

    district = Column(
        String,
        nullable=True,
    )

    language_pref = Column(
        String,
        nullable=False,
        server_default="en",
    )

    human_mode = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    extra_fields = Column(
        JSONB,
        nullable=False,
        server_default=expression.text("'{}'::jsonb"),
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
        back_populates="students",
    )

    parent = relationship(
        "ParentGuardian",
        back_populates="students",
    )

    enrollments = relationship(
        "Enrollment",
        back_populates="student",
    )

    invoices = relationship(
        "Invoice",
        back_populates="student",
    )

    message_logs = relationship(
        "MessageLog",
        back_populates="student",
    )

    escalations = relationship(
        "Escalation",
        back_populates="student",
    )

    # Memory relationships
    mem_facts = relationship("MemFact", back_populates="student")
    mem_episodes = relationship("MemEpisode", back_populates="student")
    st_turns = relationship("STTurn", back_populates="student")

    def __repr__(self):
        return (
            f"<Student(id='{self.id}', "
            f"name='{self.name}', "
            f"phone='{self.phone}')>"
        )