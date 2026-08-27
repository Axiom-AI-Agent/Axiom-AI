"""Authenticated staff dashboard Q&A — JWT only, tenant from staff row."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents.dashboard_agent import run_dashboard_agent
from api.staff_auth import StaffPrincipal

router = APIRouter(prefix="/agent", tags=["dashboard-agent"])


class DashboardAgentQueryRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


class DashboardAgentQueryResponse(BaseModel):
    reply: str
    staff_id: str
    tenant_id: str


@router.post("/query", response_model=DashboardAgentQueryResponse)
async def dashboard_agent_query(
    body: DashboardAgentQueryRequest,
    staff: StaffPrincipal,
) -> DashboardAgentQueryResponse:
    try:
        reply = await run_dashboard_agent(staff=staff, message=body.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DashboardAgentQueryResponse(
        reply=reply,
        staff_id=staff.staff_id,
        tenant_id=staff.tenant_id,
    )
