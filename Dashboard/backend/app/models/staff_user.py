from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index
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
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Key
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Staff Details
    role = Column(
        Enum(StaffRole, name="staff_role"),
        nullable=False,
        server_default="admin",
    )

    name = Column(String, nullable=False)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="staff_users")

    audit_logs = relationship(
        "AuditLog",
        back_populates="staff",
    )

    def __repr__(self):
        return (
            f"<StaffUser(id='{self.id}', "
            f"name='{self.name}', role='{self.role.value}')>"
        )