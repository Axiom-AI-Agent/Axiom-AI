"""Dashboard schedule CRUD — manage class timetables."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException

from api.schemas import (
    ExceptionCreate,
    ExceptionDeleteResponse,
    ExceptionListResponse,
    ExceptionResponse,
    ScheduleCreate,
    ScheduleDetailResponse,
    ScheduleListResponse,
    ScheduleQueryRequest,
    ScheduleQueryResponse,
    ScheduleResponse,
    ScheduleUpdate,
)
from api.tenant_scope import DashboardTenant
from domain.enums import DayOfWeek, OccurrenceStatus
from services.schedule.schedule_service import ScheduleService

router = APIRouter(
    prefix="/schedules",
    tags=["dashboard-schedules"],
)


def _to_schedule_response(raw: dict) -> ScheduleResponse:
    """Convert raw Supabase row to ScheduleResponse, mapping joined fields."""
    class_info = raw.get("subject_classes") or {}
    teacher_info = raw.get("staff_users") or {}

    return ScheduleResponse(
        id=raw["id"],
        tenant_id=raw["tenant_id"],
        class_id=raw["class_id"],
        teacher_id=raw.get("teacher_id"),
        day_of_week=raw["day_of_week"],
        start_time=str(raw["start_time"]),
        end_time=str(raw["end_time"]),
        room=raw.get("room"),
        status=raw["status"],
        effective_from=raw["effective_from"],
        effective_until=raw.get("effective_until"),
        created_at=raw.get("created_at", ""),
        updated_at=raw.get("updated_at", ""),
        class_name=class_info.get("name"),
        subject=class_info.get("subject"),
        teacher_name=teacher_info.get("name"),
    )


def _to_exception_response(raw: dict) -> ExceptionResponse:
    return ExceptionResponse(
        id=raw["id"],
        tenant_id=raw["tenant_id"],
        schedule_id=raw["schedule_id"],
        exception_date=raw["exception_date"],
        status=raw["status"],
        new_start_time=raw.get("new_start_time"),
        new_end_time=raw.get("new_end_time"),
        new_room=raw.get("new_room"),
        new_date=raw.get("new_date"),
        notes=raw.get("notes"),
        created_at=raw.get("created_at", ""),
    )


# ---------------------------------------------------------------------------
# Schedule CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=ScheduleListResponse)
async def list_schedules(
    tenant: DashboardTenant,
    class_id: str | None = None,
    teacher_id: str | None = None,
    day_of_week: DayOfWeek | None = None,
) -> ScheduleListResponse:
    svc = ScheduleService()
    rows = svc.list_schedules(
        tenant.id,
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=day_of_week,
    )
    return ScheduleListResponse(
        tenant_id=tenant.id,
        schedules=[_to_schedule_response(r) for r in rows],
    )


@router.get("/{schedule_id}", response_model=ScheduleDetailResponse)
async def get_schedule(tenant: DashboardTenant, schedule_id: str) -> ScheduleDetailResponse:
    svc = ScheduleService()
    row = svc.get_schedule(tenant.id, schedule_id)
    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleDetailResponse(
        tenant_id=tenant.id,
        schedule=_to_schedule_response(row),
    )


@router.post("", response_model=ScheduleDetailResponse, status_code=201)
async def create_schedule(
    tenant: DashboardTenant,
    body: ScheduleCreate,
) -> ScheduleDetailResponse:
    svc = ScheduleService()
    try:
        row = svc.create_schedule(
            tenant.id,
            class_id=body.class_id,
            teacher_id=body.teacher_id,
            day_of_week=body.day_of_week,
            start_time=body.start_time,
            end_time=body.end_time,
            room=body.room,
            effective_from=body.effective_from,
            effective_until=body.effective_until,
        )
    except Exception as exc:
        if "unique" in str(exc).lower():
            raise HTTPException(
                status_code=409,
                detail="A schedule already exists for this class at the same day and time",
            ) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ScheduleDetailResponse(
        tenant_id=tenant.id,
        schedule=_to_schedule_response(row),
    )


@router.patch("/{schedule_id}", response_model=ScheduleDetailResponse)
async def update_schedule(
    tenant: DashboardTenant,
    schedule_id: str,
    body: ScheduleUpdate,
) -> ScheduleDetailResponse:
    svc = ScheduleService()
    fields = body.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Convert enum values to strings
    for key in ("day_of_week", "status"):
        if key in fields and fields[key] is not None:
            fields[key] = fields[key].value

    row = svc.update_schedule(tenant.id, schedule_id, **fields)
    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return ScheduleDetailResponse(
        tenant_id=tenant.id,
        schedule=_to_schedule_response(row),
    )


@router.delete("/{schedule_id}")
async def cancel_schedule(tenant: DashboardTenant, schedule_id: str):
    svc = ScheduleService()
    row = svc.cancel_schedule(tenant.id, schedule_id)
    if not row:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"ok": True, "tenant_id": tenant.id, "schedule_id": schedule_id}


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


@router.get("/{schedule_id}/exceptions", response_model=ExceptionListResponse)
async def list_exceptions(
    tenant: DashboardTenant,
    schedule_id: str,
    exception_date: str | None = None,
) -> ExceptionListResponse:
    svc = ScheduleService()
    rows = svc.list_exceptions(tenant.id, schedule_id=schedule_id, exception_date=exception_date)
    return ExceptionListResponse(
        tenant_id=tenant.id,
        exceptions=[_to_exception_response(r) for r in rows],
    )


@router.post("/{schedule_id}/exceptions", response_model=ExceptionResponse, status_code=201)
async def create_exception(
    tenant: DashboardTenant,
    schedule_id: str,
    body: ExceptionCreate,
) -> ExceptionResponse:
    svc = ScheduleService()

    # Verify schedule exists
    schedule = svc.get_schedule(tenant.id, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    row = svc.create_exception(
        tenant.id,
        schedule_id=schedule_id,
        exception_date=body.exception_date,
        status=body.status,
        new_start_time=body.new_start_time,
        new_end_time=body.new_end_time,
        new_room=body.new_room,
        new_date=body.new_date,
        notes=body.notes,
    )
    return _to_exception_response(row)


@router.delete("/{schedule_id}/exceptions/{exception_id}")
async def delete_exception(
    tenant: DashboardTenant,
    schedule_id: str,
    exception_id: str,
):
    svc = ScheduleService()
    deleted = svc.delete_exception(tenant.id, exception_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Exception not found")
    return ExceptionDeleteResponse(tenant_id=tenant.id, exception_id=exception_id)


# ---------------------------------------------------------------------------
# Schedule queries (student-facing, date-based)
# ---------------------------------------------------------------------------


@router.post("/query/date", response_model=ScheduleQueryResponse)
async def query_schedule_for_date(
    tenant: DashboardTenant,
    target_date: str,
    body: ScheduleQueryRequest | None = None,
) -> ScheduleQueryResponse:
    """Get schedule for a specific date. Pass student_id to filter by enrollment."""
    try:
        d = date.fromisoformat(target_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    svc = ScheduleService()
    student_id = body.student_id if body else None
    rows = svc.get_schedules_for_date(tenant.id, d, student_id=student_id)

    return ScheduleQueryResponse(
        tenant_id=tenant.id,
        date=target_date,
        schedules=[_to_schedule_response(r) for r in rows],
    )


@router.post("/query/next", response_model=ScheduleDetailResponse | None)
async def query_next_class(
    tenant: DashboardTenant,
    body: ScheduleQueryRequest | None = None,
):
    """Get the next upcoming class for a student."""
    svc = ScheduleService()
    student_id = body.student_id if body else None
    row = svc.get_next_class(tenant.id, student_id=student_id)
    if not row:
        return None
    return ScheduleDetailResponse(
        tenant_id=tenant.id,
        schedule=_to_schedule_response(row),
    )


@router.post("/query/week", response_model=ScheduleQueryResponse)
async def query_week_schedule(
    tenant: DashboardTenant,
    start_date: str | None = None,
    body: ScheduleQueryRequest | None = None,
) -> ScheduleQueryResponse:
    """Get the full week schedule starting from start_date."""
    d = date.fromisoformat(start_date) if start_date else None
    svc = ScheduleService()
    student_id = body.student_id if body else None
    rows = svc.get_week_schedule(tenant.id, student_id=student_id, start_date=d)

    return ScheduleQueryResponse(
        tenant_id=tenant.id,
        date=(d or date.today()).isoformat(),
        schedules=[_to_schedule_response(r) for r in rows],
    )
