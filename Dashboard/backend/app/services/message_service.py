import uuid
from typing import Union

from sqlalchemy.orm import Session

from app.models import MessageLog
from app.models.enums import ChatChannel


def log_message(
    db: Session,
    tenant_id: str,
    student_id: str,
    channel: Union[ChatChannel, str],
    intent: str | None = None,
) -> MessageLog:
    """
    Store a message interaction.

    Shared by:
    - FastAPI routes
    - LangGraph nodes
    """

    if isinstance(channel, str):
        channel = ChatChannel(channel)

    message = MessageLog(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        student_id=student_id,
        channel=channel,
        intent=intent,
    )

    try:
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    except Exception:
        db.rollback()
        raise