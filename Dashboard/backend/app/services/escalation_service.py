import uuid

from sqlalchemy.orm import Session

from app.models import Escalation


def create_escalation(
    db: Session,
    tenant_id: str,
    student_id: str,
    reason_code: str,
) -> Escalation:
    """
    Create a new escalation for human review.

    Shared by:
    - FastAPI routes
    - LangGraph nodes
    - Future automation workflows
    """

    escalation = Escalation(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        student_id=student_id,
        reason_code=reason_code,
    )

    try:
        db.add(escalation)
        db.commit()
        db.refresh(escalation)
        return escalation

    except Exception:
        db.rollback()
        raise