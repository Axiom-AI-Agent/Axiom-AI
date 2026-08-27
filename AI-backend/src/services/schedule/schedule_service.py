"""Schedule service — timetable CRUD, queries, and centralized timezone handling.

All timezone conversion happens at the service boundary.
Database stores times in the tenant's local timezone.
Queries convert dates to tenant-local time before filtering.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from typing import Any

from loguru import logger

from domain.enums import DayOfWeek, OccurrenceStatus, ScheduleStatus
from infrastructure.db.supabase_client import get_supabase_client

# ---------------------------------------------------------------------------
# Timezone helpers (centralized)
# ---------------------------------------------------------------------------

_DEFAULT_TZ = "Asia/Colombo"


def get_tenant_timezone(tenant_id: str) -> str:
    """Fetch tenant timezone from DB. Returns default if not set."""
    client = get_supabase_client()
    resp = client.table("tenants").select("timezone").eq("id", tenant_id).limit(1).execute()
    rows = resp.data or []
    if rows and rows[0].get("timezone"):
        return str(rows[0]["timezone"])
    return _DEFAULT_TZ


def to_tenant_local_time(utc_dt: datetime, timezone: str) -> datetime:
    """Convert UTC datetime to tenant-local datetime. Centralized for all schedule queries."""
    try:
        from zoneinfo import ZoneInfo
        # If datetime is naive (no tzinfo), assume it's UTC and convert
        if utc_dt.tzinfo is None:
            # Create timezone-aware UTC datetime
            from datetime import timezone
            utc_aware = utc_dt.replace(tzinfo=timezone.utc)
            return utc_aware.astimezone(ZoneInfo(timezone))
        return utc_dt.astimezone(ZoneInfo(timezone))
    except Exception:
        # Fallback: assume UTC+5:30 for Sri Lanka if zoneinfo unavailable
        return utc_dt + timedelta(hours=5, minutes=30)


def get_tenant_now(tenant_id: str) -> datetime:
    """Get current time in tenant's local timezone."""
    utc_now = datetime.utcnow()
    tz = get_tenant_timezone(tenant_id)
    return to_tenant_local_time(utc_now, tz)


def get_tenant_today(tenant_id: str) -> date:
    """Get today's date in tenant's local timezone."""
    return get_tenant_now(tenant_id).date()


def get_day_of_week(d: date) -> DayOfWeek:
    """Convert a date to DayOfWeek enum."""
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return DayOfWeek(days[d.weekday()])


# ---------------------------------------------------------------------------
# Schedule CRUD
# ---------------------------------------------------------------------------

def _generate_id() -> str:
    return str(uuid.uuid4())


class ScheduleService:
    """Manages class schedules and exceptions. All queries are tenant-scoped."""

    def __init__(self) -> None:
        self.client = get_supabase_client()

    # --- Schedule CRUD ---

    def list_schedules(
        self,
        tenant_id: str,
        *,
        class_id: str | None = None,
        teacher_id: str | None = None,
        day_of_week: DayOfWeek | None = None,
    ) -> list[dict[str, Any]]:
        """List active schedules for a tenant, optionally filtered."""
        query = (
            self.client.table("class_schedules")
            .select("*, subject_classes(name, subject), staff_users(name)")
            .eq("tenant_id", tenant_id)
            .eq("status", ScheduleStatus.ACTIVE.value)
        )
        if class_id:
            query = query.eq("class_id", class_id)
        if teacher_id:
            query = query.eq("teacher_id", teacher_id)
        if day_of_week:
            query = query.eq("day_of_week", day_of_week.value)

        query = query.order("day_of_week").order("start_time")
        resp = query.execute()
        return resp.data or []

    def get_schedule(self, tenant_id: str, schedule_id: str) -> dict[str, Any] | None:
        """Get a single schedule by ID."""
        resp = (
            self.client.table("class_schedules")
            .select("*, subject_classes(name, subject), staff_users(name)")
            .eq("id", schedule_id)
            .eq("tenant_id", tenant_id)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else None

    def create_schedule(
        self,
        tenant_id: str,
        *,
        class_id: str,
        teacher_id: str | None = None,
        day_of_week: DayOfWeek,
        start_time: str,
        end_time: str,
        room: str | None = None,
        effective_from: str | None = None,
        effective_until: str | None = None,
    ) -> dict[str, Any]:
        """Create a new recurring schedule entry."""
        schedule_id = _generate_id()
        now = datetime.utcnow().isoformat()

        payload = {
            "id": schedule_id,
            "tenant_id": tenant_id,
            "class_id": class_id,
            "teacher_id": teacher_id,
            "day_of_week": day_of_week.value,
            "start_time": start_time,
            "end_time": end_time,
            "room": room,
            "status": ScheduleStatus.ACTIVE.value,
            "effective_from": effective_from or date.today().isoformat(),
            "effective_until": effective_until,
            "created_at": now,
            "updated_at": now,
        }

        resp = self.client.table("class_schedules").insert(payload).execute()
        logger.info("Schedule created: id={} tenant={}", schedule_id, tenant_id)
        return resp.data[0] if resp.data else payload

    def update_schedule(
        self,
        tenant_id: str,
        schedule_id: str,
        **fields: Any,
    ) -> dict[str, Any] | None:
        """Update schedule fields (partial update)."""
        if not fields:
            return self.get_schedule(tenant_id, schedule_id)

        fields["updated_at"] = datetime.utcnow().isoformat()
        resp = (
            self.client.table("class_schedules")
            .update(fields)
            .eq("id", schedule_id)
            .eq("tenant_id", tenant_id)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else None

    def cancel_schedule(self, tenant_id: str, schedule_id: str) -> dict[str, Any] | None:
        """Soft-delete a schedule by setting status to cancelled."""
        return self.update_schedule(
            tenant_id, schedule_id, status=ScheduleStatus.CANCELLED.value
        )

    # --- Exception CRUD ---

    def list_exceptions(
        self,
        tenant_id: str,
        *,
        schedule_id: str | None = None,
        exception_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """List exceptions, optionally filtered by schedule or date."""
        query = (
            self.client.table("class_schedule_exceptions")
            .select("*")
            .eq("tenant_id", tenant_id)
        )
        if schedule_id:
            query = query.eq("schedule_id", schedule_id)
        if exception_date:
            query = query.eq("exception_date", exception_date)

        query = query.order("exception_date")
        resp = query.execute()
        return resp.data or []

    def get_exception(self, tenant_id: str, exception_id: str) -> dict[str, Any] | None:
        """Get a single exception by ID."""
        resp = (
            self.client.table("class_schedule_exceptions")
            .select("*")
            .eq("id", exception_id)
            .eq("tenant_id", tenant_id)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else None

    def create_exception(
        self,
        tenant_id: str,
        *,
        schedule_id: str,
        exception_date: str,
        status: OccurrenceStatus = OccurrenceStatus.CANCELLED,
        new_start_time: str | None = None,
        new_end_time: str | None = None,
        new_room: str | None = None,
        new_date: str | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Create an exception (cancellation or reschedule)."""
        exc_id = _generate_id()

        payload = {
            "id": exc_id,
            "tenant_id": tenant_id,
            "schedule_id": schedule_id,
            "exception_date": exception_date,
            "status": status.value,
            "new_start_time": new_start_time,
            "new_end_time": new_end_time,
            "new_room": new_room,
            "new_date": new_date,
            "notes": notes,
            "created_at": datetime.utcnow().isoformat(),
        }

        resp = self.client.table("class_schedule_exceptions").insert(payload).execute()
        logger.info("Schedule exception created: id={} schedule={} date={}", exc_id, schedule_id, exception_date)
        return resp.data[0] if resp.data else payload

    def delete_exception(self, tenant_id: str, exception_id: str) -> bool:
        """Delete an exception."""
        resp = (
            self.client.table("class_schedule_exceptions")
            .delete()
            .eq("id", exception_id)
            .eq("tenant_id", tenant_id)
            .execute()
        )
        return bool(resp.data)

    # --- Schedule Queries ---

    def get_schedules_for_date(
        self,
        tenant_id: str,
        target_date: date,
        *,
        student_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get all active schedules for a specific date, with exceptions applied.

        If student_id is provided, only returns schedules for classes the student
        is enrolled in. Otherwise returns all schedules for the tenant.
        """
        day = get_day_of_week(target_date)

        # Get active schedules for this day of week
        query = (
            self.client.table("class_schedules")
            .select("*, subject_classes(name, subject), staff_users(name)")
            .eq("tenant_id", tenant_id)
            .eq("day_of_week", day.value)
            .eq("status", ScheduleStatus.ACTIVE.value)
            .lte("effective_from", target_date.isoformat())
        )

        # Filter by student's enrolled classes if provided
        if student_id:
            enrolled_class_ids = self._get_enrolled_class_ids(tenant_id, student_id)
            if not enrolled_class_ids:
                return []
            query = query.in_("class_id", enrolled_class_ids)

        resp = query.execute()
        schedules = resp.data or []

        # Apply effective_until filter in Python (NULL means no end)
        schedules = [
            s for s in schedules
            if not s.get("effective_until") or s["effective_until"] >= target_date.isoformat()
        ]

        # Get exceptions for this date
        schedule_ids = [s["id"] for s in schedules]
        if not schedule_ids:
            return []

        exc_resp = (
            self.client.table("class_schedule_exceptions")
            .select("*")
            .eq("tenant_id", tenant_id)
            .eq("exception_date", target_date.isoformat())
            .in_("schedule_id", schedule_ids)
            .execute()
        )
        exceptions = {e["schedule_id"]: e for e in (exc_resp.data or [])}

        # Apply exceptions
        result = []
        for schedule in schedules:
            exc = exceptions.get(schedule["id"])
            if exc and exc["status"] == OccurrenceStatus.CANCELLED.value:
                continue  # Skip cancelled

            entry = {**schedule}
            if exc:
                # Rescheduled — override times
                if exc.get("new_start_time"):
                    entry["start_time"] = exc["new_start_time"]
                if exc.get("new_end_time"):
                    entry["end_time"] = exc["new_end_time"]
                if exc.get("new_room"):
                    entry["room"] = exc["new_room"]
                entry["exception_notes"] = exc.get("notes")

            result.append(entry)

        # Sort by start_time
        result.sort(key=lambda x: x.get("start_time", ""))
        return result

    def get_next_class(
        self,
        tenant_id: str,
        *,
        student_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Get the student's next upcoming class from today onwards."""
        now = get_tenant_now(tenant_id)
        today = now.date()
        current_time = now.time()

        # Search today first, then next 7 days
        for days_ahead in range(8):
            check_date = today + timedelta(days=days_ahead)
            schedules = self.get_schedules_for_date(tenant_id, check_date, student_id=student_id)

            for schedule in schedules:
                # For today, only future classes
                if days_ahead == 0:
                    start = schedule.get("start_time", "")
                    if start and start <= current_time.isoformat(timespec="hours"):
                        continue
                return {**schedule, "date": check_date.isoformat()}

        return None

    def get_week_schedule(
        self,
        tenant_id: str,
        *,
        student_id: str | None = None,
        start_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Get the full week schedule starting from start_date (or today)."""
        if start_date is None:
            start_date = get_tenant_today(tenant_id)

        all_schedules = []
        for days_ahead in range(7):
            check_date = start_date + timedelta(days=days_ahead)
            day_schedules = self.get_schedules_for_date(tenant_id, check_date, student_id=student_id)
            for s in day_schedules:
                s["date"] = check_date.isoformat()
            all_schedules.extend(day_schedules)

        return all_schedules

    def _get_enrolled_class_ids(self, tenant_id: str, student_id: str) -> list[str]:
        """Get class IDs the student is enrolled in (active or pending)."""
        resp = (
            self.client.table("enrollments")
            .select("class_id")
            .eq("tenant_id", tenant_id)
            .eq("student_id", student_id)
            .in_("status", ["active", "pending"])
            .execute()
        )
        return [e["class_id"] for e in (resp.data or [])]
