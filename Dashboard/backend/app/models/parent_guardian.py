from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class ParentGuardian(Base):
    """
    Represents a student's parent or guardian.
    A parent may be linked to multiple students.
    """

    __tablename__ = "parent_guardians"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "phone",
            name="uq_parent_guardians_tenant_phone",
        ),
        Index("idx_parent_guardians_tenant_phone", "tenant_id", "phone"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Key
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Parent Details
    phone = Column(
        String,
        nullable=False,
    )

    name = Column(
        String,
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
        back_populates="parent_guardians",
    )

    students = relationship(
        "Student",
        back_populates="parent",
    )

    def __repr__(self):
        return (
            f"<ParentGuardian("
            f"id='{self.id}', "
            f"phone='{self.phone}'"
            f")>"
        )