from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Escalation
from app.models.enums import EscalationStatus
from app.schemas.schemas import (
    EscalationCreate,
    EscalationResponse,
)
from app.services.escalation_service import (
    create_escalation,
    update_escalation_status,
)
from app.websockets.escalation_manager import escalation_manager


router = APIRouter(prefix="/escalations", tags=["Escalations"])


@router.get("", response_model=List[EscalationResponse])
def get_escalations(db: Session = Depends(get_db)):
    return (
        db.query(Escalation)
        .order_by(Escalation.created_at.desc())
        .all()
    )


@router.get("/open", response_model=List[EscalationResponse])
def get_open_escalations(db: Session = Depends(get_db)):
    return (
        db.query(Escalation)
        .filter(Escalation.status == EscalationStatus.OPEN)
        .order_by(Escalation.created_at.desc())
        .all()
    )


@router.post("", response_model=EscalationResponse)
async def create_new_escalation(
    escalation_data: EscalationCreate,
    db: Session = Depends(get_db),
):
    escalation = create_escalation(
        db=db,
        tenant_id=escalation_data.tenant_id,
        student_id=escalation_data.student_id,
        reason_code=escalation_data.reason_code,
    )

    response = EscalationResponse.model_validate(escalation)
    tenant_id = cast(str, escalation.tenant_id)

    await escalation_manager.broadcast(
        tenant_id,
        {
            "type": "escalation.created",
            "escalation": response.model_dump(mode="json"),
        },
    )

    return escalation


@router.put(
    "/{escalation_id}/assign",
    response_model=EscalationResponse,
)
async def assign_escalation(
    escalation_id: str,
    db: Session = Depends(get_db),
):
    try:
        escalation = update_escalation_status(
            db=db,
            escalation_id=escalation_id,
            status=EscalationStatus.ASSIGNED,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        ) from error

    response = EscalationResponse.model_validate(escalation)
    tenant_id = cast(str, escalation.tenant_id)

    await escalation_manager.broadcast(
        tenant_id,
        {
            "type": "escalation.assigned",
            "escalation": response.model_dump(mode="json"),
        },
    )

    return escalation


@router.put(
    "/{escalation_id}/resolve",
    response_model=EscalationResponse,
)
async def resolve_escalation(
    escalation_id: str,
    db: Session = Depends(get_db),
):
    try:
        escalation = update_escalation_status(
            db=db,
            escalation_id=escalation_id,
            status=EscalationStatus.RESOLVED,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail="Escalation not found",
        ) from error

    response = EscalationResponse.model_validate(escalation)
    tenant_id = cast(str, escalation.tenant_id)

    await escalation_manager.broadcast(
        tenant_id,
        {
            "type": "escalation.resolved",
            "escalation": response.model_dump(mode="json"),
        },
    )

    return escalation