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
from app.models.enums import ChatChannel


class MessageLog(Base):
    """
    Stores metadata about conversations between students and the AI assistant.
    """

    __tablename__ = "message_logs"

    __table_args__ = (
        Index(
            "idx_message_logs_tenant_student",
            "tenant_id",
            "student_id",
            "timestamp",
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

    # Message Metadata
    channel = Column(
    Enum(
        ChatChannel,
        name="chat_channel",
        values_callable=lambda enum: [e.value for e in enum],
    ),
    nullable=False,
    server_default="twilio_whatsapp",
    )

    intent = Column(
        String,
        nullable=True,
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
        back_populates="message_logs",
    )

    student = relationship(
        "Student",
        back_populates="message_logs",
    )

    def __repr__(self):
        return (
            f"<MessageLog("
            f"id='{self.id}', "
            f"student='{self.student_id}', "
            f"channel='{self.channel.value}')>"
        )