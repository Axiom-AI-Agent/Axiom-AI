from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import Enrollment, Escalation, MessageLog, Student, SubjectClass
from app.models.enums import EnrollmentStatus, EscalationStatus
from app.schemas.schemas import (
    ClassAnalyticsComparisonResponse,
    DashboardAnalyticsResponse,
    DashboardOverviewResponse,
    EscalationActionResponse,
    EscalationsListResponse,
    MessageLogResponse,
)
from app.services.dashboard_service import (
    PAYMENT_REASON_CODES,
    TUTOR_REASON_CODE,
    build_class_analytics,
    build_dashboard_analytics,
    enrich_escalation,
    list_escalations,
    reject_payment_escalation_record,
    resolve_escalation_record,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_overview(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    open_escalations = (
        db.query(Escalation)
        .filter(
            Escalation.tenant_id == tenant_id,
            Escalation.status == EscalationStatus.OPEN,
        )
        .count()
    )

    open_payment_receipts = (
        db.query(Escalation)
        .filter(
            Escalation.tenant_id == tenant_id,
            Escalation.status == EscalationStatus.OPEN,
            Escalation.reason_code.in_(list(PAYMENT_REASON_CODES)),
        )
        .count()
    )

    open_talk_to_tutor = (
        db.query(Escalation)
        .filter(
            Escalation.tenant_id == tenant_id,
            Escalation.status == EscalationStatus.OPEN,
            Escalation.reason_code == TUTOR_REASON_CODE,
        )
        .count()
    )

    pending_enrollments = (
        db.query(Enrollment)
        .filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.status == EnrollmentStatus.PENDING,
        )
        .count()
    )

    students = (
        db.query(Student)
        .filter(Student.tenant_id == tenant_id)
        .count()
    )

    classes = (
        db.query(SubjectClass)
        .filter(SubjectClass.tenant_id == tenant_id)
        .count()
    )

    return {
        "tenant_id": tenant_id,
        "open_escalations": open_escalations,
        "open_payment_receipts": open_payment_receipts,
        "open_talk_to_tutor": open_talk_to_tutor,
        "pending_enrollments": pending_enrollments,
        "students": students,
        "classes": classes,
    }


@router.get("/summary")
def get_summary(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    overview = get_overview(
        tenant_id=tenant_id,
        db=db,
    )

    return {
        "total_students": overview["students"],
        "pending_payments": overview[
            "open_payment_receipts"
        ],
        "open_escalations": overview[
            "open_escalations"
        ],
    }


@router.get(
    "/analytics",
    response_model=DashboardAnalyticsResponse,
)
def get_dashboard_analytics(
    period: str = "7d",
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    if period not in {"today", "7d", "month"}:
        raise HTTPException(
            status_code=422,
            detail="period must be today, 7d, or month",
        )

    return build_dashboard_analytics(
        db,
        tenant_id=tenant_id,
        period=period,
    )

@router.get("/escalations", response_model=EscalationsListResponse)
def get_dashboard_escalations(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[str] = Query(None),
    reason_code: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    parsed_status = EscalationStatus(status) if status else None

    rows = list_escalations(
        db,
        tenant_id=tenant_id,
        status=parsed_status,
        reason_code=reason_code,
    )

    return {"tenant_id": tenant_id, "escalations": rows}


@router.patch(
    "/escalations/{escalation_id}/resolve",
    response_model=EscalationActionResponse,
)
def resolve_dashboard_escalation(
    escalation_id: str,
    tenant_id: str = Depends(get_tenant_id),
    reviewed_by: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        escalation, enrollment = resolve_escalation_record(
            db,
            escalation_id=escalation_id,
            tenant_id=tenant_id,
            reviewed_by=reviewed_by or "staff@demo.com",
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "ok": True,
        "escalation_id": escalation.id,
        "reason_code": escalation.reason_code,
        "resolution": escalation.resolution,
        "enrollment_status": enrollment.status.value if enrollment else None,
        "student_notified": False,
        "notification_message": None,
    }


@router.patch(
    "/escalations/{escalation_id}/reject",
    response_model=EscalationActionResponse,
)
def reject_dashboard_escalation(
    escalation_id: str,
    tenant_id: str = Depends(get_tenant_id),
    reviewed_by: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        escalation = reject_payment_escalation_record(
            db,
            escalation_id=escalation_id,
            tenant_id=tenant_id,
            reviewed_by=reviewed_by or "staff@demo.com",
        )
    except ValueError as error:
        status_code = 400 if "Only payment" in str(error) else 404
        raise HTTPException(status_code=status_code, detail=str(error)) from error

    return {
        "ok": True,
        "escalation_id": escalation.id,
        "reason_code": escalation.reason_code,
        "resolution": escalation.resolution,
        "enrollment_status": None,
        "student_notified": False,
        "notification_message": None,
    }


@router.get("/chat-logs", response_model=list[MessageLogResponse])
def get_dashboard_chat_logs(
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

@router.get(
    "/analytics/classes",
    response_model=(
        ClassAnalyticsComparisonResponse
    ),
)
def get_class_analytics(
    period: str = "7d",
    tenant_id: str = Depends(
        get_tenant_id
    ),
    db: Session = Depends(
        get_db
    ),
):
    if period not in {
        "today",
        "7d",
        "month",
    }:
        raise HTTPException(
            status_code=422,
            detail=(
                "period must be "
                "today, 7d, or month"
            ),
        )

    return build_class_analytics(
        db,
        tenant_id=tenant_id,
        period=period,
    )