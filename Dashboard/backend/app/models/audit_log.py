from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class AuditLog(Base):
    """
    Records all staff actions performed within the system.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_tenant", "tenant_id", "timestamp"),
    )

    # Primary Key
    id = Column(String, primary_key=True)

    # Foreign Keys
    tenant_id = Column(
        String,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
    )

    staff_id = Column(
        String,
        ForeignKey("staff_users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Audit Information
    action = Column(String, nullable=False)

    target_type = Column(
        String,
        nullable=False,
    )

    target_id = Column(
        String,
        nullable=False,
    )

    # Timestamp
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    tenant = relationship(
        "Tenant",
        back_populates="audit_logs",
    )

    staff = relationship(
        "StaffUser",
        back_populates="audit_logs",
    )

    def __repr__(self):
        return (
            f"<AuditLog("
            f"id='{self.id}', "
            f"action='{self.action}', "
            f"target='{self.target_type}'"
            f")>"
        )