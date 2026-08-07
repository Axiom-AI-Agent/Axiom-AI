from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.models.enums import StaffRole


class StaffUser(Base):
    """
    Represents a staff member of a tuition institute.
    """

    __tablename__ = "staff_users"

    __table_args__ = (
        Index("idx_staff_users_tenant", "tenant_id"),
        Index(
            "idx_staff_users_email",
            "email",
            unique=True,
        ),
    )

    id = Column(
        String,
        primary_key=True,
    )

    tenant_id = Column(
        String,
        ForeignKey(
            "tenants.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    role = Column(
        Enum(
            StaffRole,
            name="staff_role",
            values_callable=lambda enum: [
                item.value for item in enum
            ],
        ),
        nullable=False,
        server_default="viewer",
    )

    name = Column(
        String,
        nullable=False,
    )

    email = Column(
        String,
        nullable=False,
        unique=True,
    )

    password_hash = Column(
        String,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    tenant = relationship(
        "Tenant",
        back_populates="staff_users",
    )

    audit_logs = relationship(
        "AuditLog",
        back_populates="staff",
    )

    def __repr__(self):
        return (
            f"<StaffUser(id='{self.id}', "
            f"email='{self.email}', "
            f"role='{self.role.value}')>"
        ) 