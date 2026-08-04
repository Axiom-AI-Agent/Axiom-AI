from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.models.enums import EnrollmentStatus


class Enrollment(Base):
    """
    Represents a student's enrollment in a subject class.
    """

    __tablename__ = "enrollments"

    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "class_id",
            name="uq_enrollments_student_class",
        ),
        Index("idx_enrollments_tenant", "tenant_id"),
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

    class_id = Column(
        String,
        ForeignKey("subject_classes.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Enrollment Status
    status = Column(
        Enum(EnrollmentStatus, name="enrollment_status"),
        nullable=False,
        server_default="active",
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
        back_populates="enrollments",
    )

    student = relationship(
        "Student",
        back_populates="enrollments",
    )

    subject_class = relationship(
        "SubjectClass",
        back_populates="enrollments",
    )

    def __repr__(self):
        return (
            f"<Enrollment("
            f"id='{self.id}', "
            f"student='{self.student_id}', "
            f"class='{self.class_id}')>"
        )