from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import MessageLog, Student
from app.schemas.schemas import MessageLogCreate, MessageLogResponse
from app.services.message_service import log_message

router = APIRouter(
    prefix="/message-logs",
    tags=["Message Logs"],
)


@router.get("", response_model=List[MessageLogResponse])
def get_message_logs(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(MessageLog)
        .filter(MessageLog.tenant_id == tenant_id)
        .order_by(MessageLog.timestamp.desc())
        .all()
    )

    student_ids = [log.student_id for log in logs]
    students = {
        student.id: student
        for student in db.query(Student)
        .filter(Student.id.in_(student_ids))
        .all()
    } if student_ids else {}

    return [
        {
            "id": log.id,
            "tenant_id": log.tenant_id,
            "student_id": log.student_id,
            "student_name": students.get(log.student_id).name
            if students.get(log.student_id)
            else None,
            "channel": log.channel,
            "intent": log.intent,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


@router.post("", response_model=MessageLogResponse)
def create_message_log(
    message_data: MessageLogCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    if message_data.tenant_id != tenant_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="tenant_id mismatch")

    log = log_message(
        db=db,
        tenant_id=tenant_id,
        student_id=message_data.student_id,
        channel=message_data.channel,
        intent=message_data.intent,
    )

    student = db.query(Student).filter(Student.id == log.student_id).first()

    return {
        "id": log.id,
        "tenant_id": log.tenant_id,
        "student_id": log.student_id,
        "student_name": student.name if student else None,
        "channel": log.channel,
        "intent": log.intent,
        "timestamp": log.timestamp,
    }
