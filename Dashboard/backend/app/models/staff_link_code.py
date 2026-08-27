from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class StaffLinkCode(Base):
    """One-time dashboard code used to bind a Telegram chat to a staff account."""

    __tablename__ = "staff_link_codes"

    __table_args__ = (
        Index("idx_staff_link_codes_lookup", "tenant_id", "code"),
    )

    id = Column(String, primary_key=True)
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
    code = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    staff = relationship("StaffUser", back_populates="link_codes")
