from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import MessageLog
from app.schemas.schemas import (
    MessageLogCreate,
    MessageLogResponse,
)
from app.services.message_service import log_message

router = APIRouter(
    prefix="/message-logs",
    tags=["Message Logs"],
)


@router.get("", response_model=List[MessageLogResponse])
def get_message_logs(db: Session = Depends(get_db)):
    return db.query(MessageLog).all()


@router.post("", response_model=MessageLogResponse)
def create_message_log(
    message_data: MessageLogCreate,
    db: Session = Depends(get_db),
):
    return log_message(
        db=db,
        tenant_id=message_data.tenant_id,
        student_id=message_data.student_id,
        channel=message_data.channel,
        intent=message_data.intent,
    )