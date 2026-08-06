from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models import Enrollment, Escalation, Invoice, Student, SubjectClass
from app.models.enums import EnrollmentStatus, EscalationStatus, InvoiceStatus


PAYMENT_REASON_CODES = {"payment_receipt", "enrollment_payment_review"}
TUTOR_REASON_CODE = "talk_to_tutor"


def is_payment_reason(reason_code: str) -> bool:
    return reason_code in PAYMENT_REASON_CODES


def enrich_escalation(escalation: Escalation) -> dict:
    student = escalation.student
    return {
        "id": escalation.id,
        "tenant_id": escalation.tenant_id,
        "student_id": escalation.student_id,
        "student_name": student.name if student else None,
        "student_phone": student.phone if student else None,
        "enrollment_id": escalation.enrollment_id,
        "reason_code": escalation.reason_code,
        "status": escalation.status,
        "student_message": escalation.student_message,
        "media_url": escalation.media_url,
        "resolution": escalation.resolution,
        "reviewed_by": escalation.reviewed_by,
        "reviewed_at": escalation.reviewed_at,
        "created_at": escalation.created_at,
        "updated_at": escalation.updated_at,
    }


def list_escalations(
    db: Session,
    *,
    tenant_id: str,
    status: EscalationStatus | None = None,
    reason_code: str | None = None,
) -> list[dict]:
    query = (
        db.query(Escalation)
        .options(joinedload(Escalation.student))
        .filter(Escalation.tenant_id == tenant_id)
        .order_by(Escalation.created_at.desc())
    )

    if status is not None:
        query = query.filter(Escalation.status == status)

    if reason_code is not None:
        query = query.filter(Escalation.reason_code == reason_code)

    return [enrich_escalation(row) for row in query.all()]


def _activate_payment_enrollment(
    db: Session,
    escalation: Escalation,
) -> Enrollment | None:
    enrollment: Enrollment | None = None

    if escalation.enrollment_id:
        enrollment = (
            db.query(Enrollment)
            .filter(Enrollment.id == escalation.enrollment_id)
            .first()
        )

    if enrollment is None:
        enrollment = (
            db.query(Enrollment)
            .filter(
                Enrollment.tenant_id == escalation.tenant_id,
                Enrollment.student_id == escalation.student_id,
                Enrollment.status == EnrollmentStatus.PENDING,
            )
            .order_by(Enrollment.created_at.desc())
            .first()
        )

    if enrollment is not None:
        enrollment.status = EnrollmentStatus.ACTIVE  # type: ignore[assignment]

    pending_invoice = (
        db.query(Invoice)
        .filter(
            Invoice.tenant_id == escalation.tenant_id,
            Invoice.student_id == escalation.student_id,
            Invoice.status == InvoiceStatus.PENDING,
        )
        .order_by(Invoice.created_at.desc())
        .first()
    )

    if pending_invoice is not None:
        pending_invoice.status = InvoiceStatus.PAID  # type: ignore[assignment]

    return enrollment


def resolve_escalation_record(
    db: Session,
    *,
    escalation_id: str,
    tenant_id: str,
    reviewed_by: str | None = None,
) -> tuple[Escalation, Enrollment | None]:
    escalation = (
        db.query(Escalation)
        .options(joinedload(Escalation.student))
        .filter(
            Escalation.id == escalation_id,
            Escalation.tenant_id == tenant_id,
        )
        .first()
    )

    if escalation is None:
        raise ValueError("Escalation not found")

    now = datetime.now(timezone.utc)
    enrollment: Enrollment | None = None
    resolution = "closed"

    if is_payment_reason(escalation.reason_code):
        enrollment = _activate_payment_enrollment(db, escalation)
        resolution = "approved"

    escalation.status = EscalationStatus.RESOLVED  # type: ignore[assignment]
    escalation.resolution = resolution  # type: ignore[assignment]
    escalation.reviewed_by = reviewed_by  # type: ignore[assignment]
    escalation.reviewed_at = now  # type: ignore[assignment]

    db.commit()
    db.refresh(escalation)

    return escalation, enrollment


def reject_payment_escalation_record(
    db: Session,
    *,
    escalation_id: str,
    tenant_id: str,
    reviewed_by: str | None = None,
) -> Escalation:
    escalation = (
        db.query(Escalation)
        .options(joinedload(Escalation.student))
        .filter(
            Escalation.id == escalation_id,
            Escalation.tenant_id == tenant_id,
        )
        .first()
    )

    if escalation is None:
        raise ValueError("Escalation not found")

    if not is_payment_reason(escalation.reason_code):
        raise ValueError("Only payment escalations can be rejected")

    now = datetime.now(timezone.utc)
    escalation.status = EscalationStatus.RESOLVED  # type: ignore[assignment]
    escalation.resolution = "rejected"  # type: ignore[assignment]
    escalation.reviewed_by = reviewed_by  # type: ignore[assignment]
    escalation.reviewed_at = now  # type: ignore[assignment]

    db.commit()
    db.refresh(escalation)

    return escalation


def student_enrollment_summaries(
    db: Session,
    student_ids: list[str],
) -> dict[str, list[dict]]:
    if not student_ids:
        return {}

    rows = (
        db.query(Enrollment)
        .options(joinedload(Enrollment.subject_class))
        .filter(Enrollment.student_id.in_(student_ids))
        .all()
    )

    grouped: dict[str, list[dict]] = {student_id: [] for student_id in student_ids}

    for row in rows:
        subject_class: SubjectClass | None = row.subject_class
        grouped[row.student_id].append(
            {
                "id": row.id,
                "class_id": row.class_id,
                "class_subject": subject_class.subject if subject_class else None,
                "class_name": subject_class.name if subject_class else None,
                "status": row.status,
                "created_at": row.created_at,
            }
        )

    return grouped


def enrich_student(db: Session, student: Student) -> dict:
    enrollments = student_enrollment_summaries(db, [student.id]).get(student.id, [])
    return {
        "id": student.id,
        "tenant_id": student.tenant_id,
        "name": student.name,
        "phone": student.phone,
        "district": student.district,
        "language_pref": student.language_pref,
        "created_at": student.created_at,
        "updated_at": student.updated_at,
        "enrollments": enrollments,
    }
