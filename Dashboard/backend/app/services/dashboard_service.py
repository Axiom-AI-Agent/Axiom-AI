from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models import (
    Enrollment,
    Escalation,
    Invoice,
    Student,
    SubjectClass,
    STTurn,
)
from app.models.enums import (
    EnrollmentStatus,
    EscalationStatus,
    InvoiceStatus,
    MessageRole,
)

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

def build_dashboard_analytics(
    db: Session,
    *,
    tenant_id: str,
    estimated_minutes_per_deflection: int = 2,
) -> dict:
    turns = (
        db.query(STTurn)
        .filter(STTurn.tenant_id == tenant_id)
        .order_by(
            STTurn.session_id.asc(),
            STTurn.created_at.asc(),
        )
        .all()
    )

    escalations = (
        db.query(Escalation)
        .filter(Escalation.tenant_id == tenant_id)
        .all()
    )

    students = (
        db.query(Student)
        .filter(Student.tenant_id == tenant_id)
        .all()
    )

    students_by_id = {
        student.id: student
        for student in students
    }

    total_messages = len(turns)

    session_ids = {
        turn.session_id
        for turn in turns
        if turn.session_id
    }

    total_conversations = len(session_ids)

    # Current escalation table does not store session_id.
    # Student-based proxy is used until exact session-level
    # escalation attribution is introduced.
    escalated_student_ids = {
        escalation.student_id
        for escalation in escalations
    }

    sessions_by_student: dict[str, set[str]] = defaultdict(set)

    for turn in turns:
        if turn.user_id and turn.session_id:
            sessions_by_student[
                turn.user_id
            ].add(turn.session_id)

    escalated_conversation_proxy = sum(
        len(sessions_by_student.get(student_id, set()))
        for student_id in escalated_student_ids
    )

    escalated_conversation_proxy = min(
        escalated_conversation_proxy,
        total_conversations,
    )

    deflected_conversations = max(
        total_conversations
        - escalated_conversation_proxy,
        0,
    )

    if total_conversations > 0:
        deflection_rate = round(
            (
                deflected_conversations
                / total_conversations
            )
            * 100,
            1,
        )
    else:
        deflection_rate = 0.0

    # Calculate user -> next assistant latency per session.
    response_times: list[float] = []

    grouped_turns: dict[str, list[STTurn]] = defaultdict(list)

    for turn in turns:
        grouped_turns[
            turn.session_id
        ].append(turn)

    for session_turns in grouped_turns.values():
        for index, turn in enumerate(session_turns):
            if turn.role != MessageRole.USER:
                continue

            for next_turn in session_turns[
                index + 1 :
            ]:
                if (
                    next_turn.role
                    == MessageRole.ASSISTANT
                ):
                    if (
                        turn.created_at
                        and next_turn.created_at
                    ):
                        delta = (
                            next_turn.created_at
                            - turn.created_at
                        ).total_seconds()

                        if delta >= 0:
                            response_times.append(
                                delta
                            )

                    break

                if (
                    next_turn.role
                    == MessageRole.USER
                ):
                    break

    average_response_seconds = (
        round(
            sum(response_times)
            / len(response_times),
            2,
        )
        if response_times
        else 0.0
    )

    total_escalations = len(escalations)

    open_escalations = sum(
        1
        for escalation in escalations
        if escalation.status
        == EscalationStatus.OPEN
    )

    resolved_escalations = sum(
        1
        for escalation in escalations
        if escalation.status
        == EscalationStatus.RESOLVED
    )

    category_counts: dict[str, int] = defaultdict(int)

    for escalation in escalations:
        category_counts[
            escalation.reason_code
        ] += 1

    escalation_categories = [
        {
            "reason_code": reason_code,
            "count": count,
        }
        for reason_code, count
        in sorted(
            category_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    message_counts: dict[str, int] = defaultdict(int)
    conversation_counts: dict[str, set[str]] = defaultdict(set)
    escalation_counts: dict[str, int] = defaultdict(int)

    for turn in turns:
        message_counts[
            turn.user_id
        ] += 1

        if turn.session_id:
            conversation_counts[
                turn.user_id
            ].add(turn.session_id)

    for escalation in escalations:
        escalation_counts[
            escalation.student_id
        ] += 1

    all_student_ids = set(
        message_counts.keys()
    ) | set(
        escalation_counts.keys()
    )

    student_metrics = []

    for student_id in all_student_ids:
        student = students_by_id.get(
            student_id
        )

        student_metrics.append(
            {
                "student_id": student_id,
                "student_name": (
                    student.name
                    if student
                    else None
                ),
                "messages": message_counts.get(
                    student_id,
                    0,
                ),
                "conversations": len(
                    conversation_counts.get(
                        student_id,
                        set(),
                    )
                ),
                "escalations": escalation_counts.get(
                    student_id,
                    0,
                ),
            }
        )

    student_metrics.sort(
        key=lambda row: (
            row["messages"],
            row["conversations"],
        ),
        reverse=True,
    )

    estimated_minutes_saved = (
        deflected_conversations
        * estimated_minutes_per_deflection
    )

    return {
        "tenant_id": tenant_id,
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "deflected_conversations": (
            deflected_conversations
        ),
        "deflection_rate": deflection_rate,
        "average_response_seconds": (
            average_response_seconds
        ),
        "estimated_minutes_saved": (
            estimated_minutes_saved
        ),
        "total_escalations": total_escalations,
        "open_escalations": open_escalations,
        "resolved_escalations": (
            resolved_escalations
        ),
        "escalation_categories": (
            escalation_categories
        ),
        "students": student_metrics,
    }

def build_class_analytics(
    db: Session,
    *,
    tenant_id: str,
    estimated_minutes_per_deflection: int = 2,
) -> dict:
    classes = (
        db.query(SubjectClass)
        .filter(
            SubjectClass.tenant_id == tenant_id
        )
        .order_by(
            SubjectClass.subject.asc(),
            SubjectClass.name.asc(),
        )
        .all()
    )

    enrollments = (
        db.query(Enrollment)
        .filter(
            Enrollment.tenant_id == tenant_id
        )
        .all()
    )

    turns = (
        db.query(STTurn)
        .filter(
            STTurn.tenant_id == tenant_id
        )
        .order_by(
            STTurn.session_id.asc(),
            STTurn.created_at.asc(),
        )
        .all()
    )

    escalations = (
        db.query(Escalation)
        .filter(
            Escalation.tenant_id == tenant_id
        )
        .all()
    )

    class_enrollments = defaultdict(list)

    for enrollment in enrollments:
        class_enrollments[
            enrollment.class_id
        ].append(enrollment)

    turns_by_student = defaultdict(list)

    for turn in turns:
        turns_by_student[
            turn.user_id
        ].append(turn)

    escalations_by_student = defaultdict(list)

    for escalation in escalations:
        escalations_by_student[
            escalation.student_id
        ].append(escalation)

    results = []

    for subject_class in classes:
        class_rows = (
            class_enrollments.get(
                subject_class.id,
                [],
            )
        )

        student_ids = {
            row.student_id
            for row in class_rows
        }

        active_students = sum(
            1
            for row in class_rows
            if row.status
            == EnrollmentStatus.ACTIVE
        )

        pending_students = sum(
            1
            for row in class_rows
            if row.status
            == EnrollmentStatus.PENDING
        )

        class_turns = []

        for student_id in student_ids:
            class_turns.extend(
                turns_by_student.get(
                    student_id,
                    [],
                )
            )

        class_escalations = []

        for student_id in student_ids:
            class_escalations.extend(
                escalations_by_student.get(
                    student_id,
                    [],
                )
            )

        session_ids = {
            turn.session_id
            for turn in class_turns
            if turn.session_id
        }

        total_conversations = len(
            session_ids
        )

        total_messages = len(
            class_turns
        )

        grouped_turns = defaultdict(list)

        for turn in class_turns:
            grouped_turns[
                turn.session_id
            ].append(turn)

        response_times = []

        for session_turns in (
            grouped_turns.values()
        ):
            session_turns.sort(
                key=lambda row:
                    row.created_at
            )

            for index, turn in enumerate(
                session_turns
            ):
                if (
                    turn.role
                    != MessageRole.USER
                ):
                    continue

                for next_turn in (
                    session_turns[
                        index + 1 :
                    ]
                ):
                    if (
                        next_turn.role
                        == MessageRole.ASSISTANT
                    ):
                        if (
                            turn.created_at
                            and next_turn.created_at
                        ):
                            seconds = (
                                next_turn.created_at
                                - turn.created_at
                            ).total_seconds()

                            if seconds >= 0:
                                response_times.append(
                                    seconds
                                )

                        break

                    if (
                        next_turn.role
                        == MessageRole.USER
                    ):
                        break

        average_response_seconds = (
            round(
                sum(response_times)
                / len(response_times),
                2,
            )
            if response_times
            else 0.0
        )

        total_escalations = len(
            class_escalations
        )

        open_escalations = sum(
            1
            for escalation
            in class_escalations
            if escalation.status
            == EscalationStatus.OPEN
        )

        resolved_escalations = sum(
            1
            for escalation
            in class_escalations
            if escalation.status
            == EscalationStatus.RESOLVED
        )

        escalated_student_ids = {
            escalation.student_id
            for escalation
            in class_escalations
        }

        escalated_sessions = set()

        for student_id in (
            escalated_student_ids
        ):
            for turn in turns_by_student.get(
                student_id,
                [],
            ):
                if turn.session_id:
                    escalated_sessions.add(
                        turn.session_id
                    )

        escalated_conversation_proxy = min(
            len(escalated_sessions),
            total_conversations,
        )

        deflected_conversations = max(
            total_conversations
            - escalated_conversation_proxy,
            0,
        )

        deflection_rate = (
            round(
                (
                    deflected_conversations
                    / total_conversations
                )
                * 100,
                1,
            )
            if total_conversations
            else 0.0
        )

        estimated_minutes_saved = (
            deflected_conversations
            * estimated_minutes_per_deflection
        )

        results.append(
            {
                "class_id":
                    subject_class.id,
                "class_name":
                    subject_class.name,
                "subject":
                    subject_class.subject,
                "grade":
                    subject_class.grade,
                "enrolled_students":
                    len(student_ids),
                "active_students":
                    active_students,
                "pending_students":
                    pending_students,
                "total_messages":
                    total_messages,
                "total_conversations":
                    total_conversations,
                "deflected_conversations":
                    deflected_conversations,
                "deflection_rate":
                    deflection_rate,
                "average_response_seconds":
                    average_response_seconds,
                "estimated_minutes_saved":
                    estimated_minutes_saved,
                "total_escalations":
                    total_escalations,
                "open_escalations":
                    open_escalations,
                "resolved_escalations":
                    resolved_escalations,
            }
        )

    return {
        "tenant_id": tenant_id,
        "attribution_mode":
            "enrollment_membership",
        "classes": results,
    }