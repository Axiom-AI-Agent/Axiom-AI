from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.models.enums import ChatChannel


class StaffChannel(Base):
    """Links a staff member to a messaging channel address (e.g. Telegram chat_id)."""

    __tablename__ = "staff_channels"

    __table_args__ = (
        UniqueConstraint("tenant_id", "channel", "channel_address"),
        UniqueConstraint("staff_id", "channel"),
        Index("idx_staff_channels_lookup", "tenant_id", "channel", "channel_address"),
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
    channel = Column(
        Enum(
            ChatChannel,
            name="chat_channel",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    channel_address = Column(String, nullable=False)
    is_primary = Column(Boolean, nullable=False, default=True, server_default="true")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    staff = relationship("StaffUser", back_populates="channels")
