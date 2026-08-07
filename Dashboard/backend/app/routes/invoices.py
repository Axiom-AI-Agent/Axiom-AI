from typing import List, cast

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.deps.tenant import get_tenant_id
from app.models import Escalation, Student
from app.models.enums import EscalationStatus
from app.schemas.schemas import (
    EscalationCreate,
    EscalationResponse,
)
from app.services.escalation_service import (
    create_escalation,
)
from app.websockets.escalation_manager import (
    escalation_manager,
)


router = APIRouter(
    prefix="/escalations",
    tags=["Escalations"],
)


def get_tenant_escalation_or_404(
    db: Session,
    escalation_id: str,
    tenant_id: str,
) -> Escalation:
    escalation = (
        db.query(Escalation)
        .filter(
            Escalation.id
            == escalation_id,
            Escalation.tenant_id
            == tenant_id,
        )
        .first()
    )

    if escalation is None:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        )

    return escalation


def serialize_escalation(
    db: Session,
    escalation: Escalation,
) -> dict:
    student = (
        db.query(Student)
        .filter(
            Student.id
            == escalation.student_id,
            Student.tenant_id
            == escalation.tenant_id,
        )
        .first()
    )

    return {
        "id": escalation.id,
        "tenant_id":
            escalation.tenant_id,
        "student_id":
            escalation.student_id,
        "student_name":
            student.name
            if student
            else None,
        "student_phone":
            student.phone
            if student
            else None,
        "enrollment_id":
            escalation.enrollment_id,
        "reason_code":
            escalation.reason_code,
        "status":
            escalation.status,
        "student_message":
            escalation.student_message,
        "media_url":
            escalation.media_url,
        "resolution":
            escalation.resolution,
        "reviewed_by":
            escalation.reviewed_by,
        "reviewed_at":
            escalation.reviewed_at,
        "created_at":
            escalation.created_at,
        "updated_at":
            escalation.updated_at,
    }


@router.get(
    "",
    response_model=List[
        EscalationResponse
    ],
)
def get_escalations(
    tenant_id: str = Depends(
        get_tenant_id
    ),
    db: Session = Depends(
        get_db
    ),
):
    escalations = (
        db.query(Escalation)
        .filter(
            Escalation.tenant_id
            == tenant_id,
        )
        .order_by(
            Escalation.created_at.desc()
        )
        .all()
    )

    return [
        serialize_escalation(
            db,
            escalation,
        )
        for escalation
        in escalations
    ]


@router.get(
    "/open",
    response_model=List[
        EscalationResponse
    ],
)
def get_open_escalations(
    tenant_id: str = Depends(
        get_tenant_id
    ),
    db: Session = Depends(
        get_db
    ),
):
    escalations = (
        db.query(Escalation)
        .filter(
            Escalation.tenant_id
            == tenant_id,
            Escalation.status
            == EscalationStatus.OPEN,
        )
        .order_by(
            Escalation.created_at.desc()
        )
        .all()
    )

    return [
        serialize_escalation(
            db,
            escalation,
        )
        for escalation
        in escalations
    ]


@router.post(
    "",
    response_model=
        EscalationResponse,
    status_code=201,
)
async def create_new_escalation(
    escalation_data:
        EscalationCreate,
    tenant_id: str = Depends(
        get_tenant_id
    ),
    db: Session = Depends(
        get_db
    ),
):
    if (
        escalation_data.tenant_id
        != tenant_id
    ):
        raise HTTPException(
            status_code=403,
            detail="tenant_id mismatch",
        )

    student = (
        db.query(Student)
        .filter(
            Student.id
            == escalation_data.student_id,
            Student.tenant_id
            == tenant_id,
        )
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )

    escalation = (
        create_escalation(
            db=db,
            tenant_id=tenant_id,
            student_id=(
                escalation_data
                .student_id
            ),
            reason_code=(
                escalation_data
                .reason_code
            ),
        )
    )

    response_data = (
        serialize_escalation(
            db,
            escalation,
        )
    )

    response = (
        EscalationResponse(
            **response_data
        )
    )

    await escalation_manager.broadcast(
        tenant_id,
        {
            "type":
                "escalation.created",
            "escalation":
                response.model_dump(
                    mode="json"
                ),
        },
    )

    return response_data


@router.put(
    "/{escalation_id}/assign",
    response_model=
        EscalationResponse,
)
async def assign_escalation(
    escalation_id: str,
    tenant_id: str = Depends(
        get_tenant_id
    ),
    db: Session = Depends(
        get_db
    ),
):
    escalation = (
        get_tenant_escalation_or_404(
            db,
            escalation_id,
            tenant_id,
        )
    )

    escalation.status = (
        EscalationStatus.ASSIGNED
    )  # type: ignore

    db.commit()
    db.refresh(escalation)

    response_data = (
        serialize_escalation(
            db,
            escalation,
        )
    )

    response = (
        EscalationResponse(
            **response_data
        )
    )

    websocket_tenant_id = cast(
        str,
        escalation.tenant_id,
    )

    await escalation_manager.broadcast(
        websocket_tenant_id,
        {
            "type":
                "escalation.assigned",
            "escalation":
                response.model_dump(
                    mode="json"
                ),
        },
    )

    return response_data


@router.put(
    "/{escalation_id}/resolve",
    response_model=
        EscalationResponse,
)
async def resolve_escalation(
    escalation_id: str,
    tenant_id: str = Depends(
        get_tenant_id
    ),
    db: Session = Depends(
        get_db
    ),
):
    escalation = (
        get_tenant_escalation_or_404(
            db,
            escalation_id,
            tenant_id,
        )
    )

    escalation.status = (
        EscalationStatus.RESOLVED
    )  # type: ignore

    db.commit()
    db.refresh(escalation)

    response_data = (
        serialize_escalation(
            db,
            escalation,
        )
    )

    response = (
        EscalationResponse(
            **response_data
        )
    )

    websocket_tenant_id = cast(
        str,
        escalation.tenant_id,
    )

    await escalation_manager.broadcast(
        websocket_tenant_id,
        {
            "type":
                "escalation.resolved",
            "escalation":
                response.model_dump(
                    mode="json"
                ),
        },
    )

    return response_data