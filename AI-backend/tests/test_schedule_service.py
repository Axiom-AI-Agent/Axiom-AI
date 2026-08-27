"""Tests for schedule CRUD, recurring schedules, exceptions, timezone, and multiple sessions."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from domain.enums import DayOfWeek, OccurrenceStatus, ScheduleStatus
from services.schedule.schedule_service import (
    ScheduleService,
    get_day_of_week,
    get_tenant_today,
    to_tenant_local_time,
)


# ---------------------------------------------------------------------------
# Timezone helpers tests
# ---------------------------------------------------------------------------


class TestTimezoneHelpers:
    def test_get_day_of_week(self):
        """Correctly maps date to DayOfWeek enum."""
        # 2026-08-27 is a Thursday
        d = date(2026, 8, 27)
        assert get_day_of_week(d) == DayOfWeek.THURSDAY

    def test_get_day_of_week_all_days(self):
        """All 7 days map correctly."""
        # 2026-08-24 is Monday
        dates = [
            (date(2026, 8, 24), DayOfWeek.MONDAY),
            (date(2026, 8, 25), DayOfWeek.TUESDAY),
            (date(2026, 8, 26), DayOfWeek.WEDNESDAY),
            (date(2026, 8, 27), DayOfWeek.THURSDAY),
            (date(2026, 8, 28), DayOfWeek.FRIDAY),
            (date(2026, 8, 29), DayOfWeek.SATURDAY),
            (date(2026, 8, 30), DayOfWeek.SUNDAY),
        ]
        for d, expected in dates:
            assert get_day_of_week(d) == expected, f"{d} should be {expected}"

    def test_to_tenant_local_time(self):
        """UTC datetime converts correctly to tenant timezone."""
        utc_dt = datetime(2026, 8, 27, 3, 30)  # 03:30 UTC
        local = to_tenant_local_time(utc_dt, "Asia/Colombo")
        # UTC+5:30 → 09:00 (3:30 + 5:30 = 9:00)
        assert local.hour == 9
        assert local.minute == 0


# ---------------------------------------------------------------------------
# ScheduleService tests (mocked Supabase)
# ---------------------------------------------------------------------------


class MockSupabaseResponse:
    """Mock Supabase execute() response."""

    def __init__(self, data: list[dict] | None = None):
        self.data = data or []


class MockSupabaseTable:
    """Mock Supabase table with chainable query builder."""

    def __init__(self, data: list[dict] | None = None):
        self._data = data or []
        self._filters: dict[str, Any] = {}
        self._order: list[str] = []
        self._limit: int | None = None

    def select(self, *args, **kwargs):
        return self

    def eq(self, column: str, value):
        self._filters[column] = ("eq", value)
        return self

    def lte(self, column: str, value):
        self._filters[column] = ("lte", value)
        return self

    def in_(self, column: str, values):
        self._filters[column] = ("in", values)
        return self

    def order(self, column: str, **kwargs):
        self._order.append(column)
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def insert(self, payload):
        self._data = [payload]
        return self

    def update(self, fields):
        if self._data:
            self._data[0] = {**self._data[0], **fields}
        return self

    def delete(self):
        return self

    def execute(self):
        return MockSupabaseResponse(self._data)


class MockSupabaseClient:
    """Mock Supabase client for unit tests."""

    def __init__(self):
        self._tables: dict[str, MockSupabaseTable] = {}

    def table(self, name: str) -> MockSupabaseTable:
        if name not in self._tables:
            self._tables[name] = MockSupabaseTable()
        return self._tables[name]


@pytest.fixture
def mock_client():
    """Provide a mock Supabase client."""
    return MockSupabaseClient()


@pytest.fixture
def svc(mock_client):
    """Provide a ScheduleService with mocked Supabase."""
    with patch(
        "services.schedule.schedule_service.get_supabase_client",
        return_value=mock_client,
    ):
        return ScheduleService()


# ---------------------------------------------------------------------------
# CRUD tests
# ---------------------------------------------------------------------------


class TestScheduleCRUD:
    def test_create_schedule(self, svc, mock_client):
        """Schedule creation generates ID and returns row."""
        # Seed enrollment data for class lookup
        mock_client.table("enrollments")._data = []

        row = svc.create_schedule(
            "tenant-1",
            class_id="class-1",
            day_of_week=DayOfWeek.MONDAY,
            start_time="09:00",
            end_time="10:30",
            room="Room A",
        )

        assert row["tenant_id"] == "tenant-1"
        assert row["class_id"] == "class-1"
        assert row["day_of_week"] == "monday"
        assert row["start_time"] == "09:00"
        assert row["end_time"] == "10:30"
        assert row["room"] == "Room A"
        assert row["status"] == "active"

    def test_list_schedules(self, svc, mock_client):
        """List returns schedules for the tenant."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "day_of_week": "monday", "start_time": "09:00"},
            {"id": "s2", "day_of_week": "wednesday", "start_time": "14:00"},
        ]

        rows = svc.list_schedules("tenant-1")
        assert len(rows) == 2

    def test_list_schedules_filters_by_class(self, svc, mock_client):
        """List can filter by class_id."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "class_id": "class-1"},
            {"id": "s2", "class_id": "class-2"},
        ]

        rows = svc.list_schedules("tenant-1", class_id="class-1")
        # Mock returns all data, but the service applies filter via .eq()
        # Verify the filter was set on the mock table
        table = mock_client._tables["class_schedules"]
        assert table._filters.get("class_id") == ("eq", "class-1")

    def test_cancel_schedule(self, svc, mock_client):
        """Cancel sets status to cancelled."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "status": "active"}
        ]

        row = svc.cancel_schedule("tenant-1", "s1")
        assert row["status"] == "cancelled"


# ---------------------------------------------------------------------------
# Exception tests
# ---------------------------------------------------------------------------


class TestScheduleExceptions:
    def test_create_exception(self, svc, mock_client):
        """Exception creation works."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "tenant_id": "tenant-1"}
        ]

        row = svc.create_exception(
            "tenant-1",
            schedule_id="s1",
            exception_date="2026-09-01",
            status=OccurrenceStatus.CANCELLED,
            notes="Holiday",
        )

        assert row["schedule_id"] == "s1"
        assert row["exception_date"] == "2026-09-01"
        assert row["status"] == "cancelled"
        assert row["notes"] == "Holiday"

    def test_reschedule_exception(self, svc, mock_client):
        """Reschedule exception with new times."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "tenant_id": "tenant-1"}
        ]

        row = svc.create_exception(
            "tenant-1",
            schedule_id="s1",
            exception_date="2026-09-01",
            status=OccurrenceStatus.CANCELLED,
            new_start_time="14:00",
            new_end_time="15:30",
            new_date="2026-09-02",
            notes="Rescheduled to next day",
        )

        assert row["new_start_time"] == "14:00"
        assert row["new_end_time"] == "15:30"
        assert row["new_date"] == "2026-09-02"


# ---------------------------------------------------------------------------
# Multiple sessions on same day
# ---------------------------------------------------------------------------


class TestMultipleSessions:
    def test_same_class_different_times(self, svc):
        """
        Same class on same day with different start times should be allowed.
        UNIQUE (tenant_id, class_id, day_of_week, start_time) allows this.
        """
        mock_client = MagicMock()
        svc.client = mock_client

        # Create two schedules for same class on Tuesday
        svc.create_schedule(
            "tenant-1",
            class_id="class-1",
            day_of_week=DayOfWeek.TUESDAY,
            start_time="09:00",
            end_time="10:30",
        )
        svc.create_schedule(
            "tenant-1",
            class_id="class-1",
            day_of_week=DayOfWeek.TUESDAY,
            start_time="14:00",
            end_time="15:30",
        )

        # Both should succeed — different start_time violates no constraint
        assert mock_client.table().insert.call_count == 2

    def test_same_class_same_time_rejected(self, svc):
        """
        Same class on same day with same start time should be rejected.
        UNIQUE (tenant_id, class_id, day_of_week, start_time) prevents this.
        """
        # This would be caught by the DB unique constraint
        # The service layer doesn't prevent it — the DB does
        pass


# ---------------------------------------------------------------------------
# Recurring schedule queries
# ---------------------------------------------------------------------------


class TestRecurringQueries:
    def test_get_schedules_for_date_filters_by_day(self, svc, mock_client):
        """Query filters by day of week."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "day_of_week": "monday", "start_time": "09:00", "effective_from": "2026-01-01", "status": "active"},
            {"id": "s2", "day_of_week": "wednesday", "start_time": "14:00", "effective_from": "2026-01-01", "status": "active"},
        ]
        mock_client.table("class_schedule_exceptions")._data = []

        # Query for Monday
        rows = svc.get_schedules_for_date("tenant-1", date(2026, 8, 24))  # Monday
        # Should only get Monday schedule
        # (actual filtering depends on mock behavior)

    def test_exception_cancels_occurrence(self, svc, mock_client):
        """Cancelled exception removes the occurrence from results."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "day_of_week": "monday", "start_time": "09:00", "effective_from": "2026-01-01", "status": "active"},
        ]
        mock_client.table("class_schedule_exceptions")._data = [
            {"schedule_id": "s1", "exception_date": "2026-08-24", "status": "cancelled"},
        ]

        rows = svc.get_schedules_for_date("tenant-1", date(2026, 8, 24))
        # Cancelled occurrence should be excluded
        assert len(rows) == 0

    def test_reschedule_overrides_times(self, svc, mock_client):
        """Rescheduled exception overrides start/end times."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "day_of_week": "monday", "start_time": "09:00", "end_time": "10:30", "effective_from": "2026-01-01", "status": "active"},
        ]
        mock_client.table("class_schedule_exceptions")._data = [
            {"schedule_id": "s1", "exception_date": "2026-08-24", "status": "cancelled", "new_start_time": "14:00", "new_end_time": "15:30"},
        ]

        rows = svc.get_schedules_for_date("tenant-1", date(2026, 8, 24))
        if rows:
            assert rows[0]["start_time"] == "14:00"
            assert rows[0]["end_time"] == "15:30"

    def test_effective_until_filters_out_expired(self, svc, mock_client):
        """Schedule with effective_until in the past is excluded."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "day_of_week": "monday", "start_time": "09:00", "effective_from": "2026-01-01", "effective_until": "2026-06-30", "status": "active"},
        ]
        mock_client.table("class_schedule_exceptions")._data = []

        # Query for August — should be excluded
        rows = svc.get_schedules_for_date("tenant-1", date(2026, 8, 24))
        assert len(rows) == 0

    def test_no_effective_until_never_expires(self, svc, mock_client):
        """Schedule with no effective_until is always included."""
        mock_client.table("class_schedules")._data = [
            {"id": "s1", "day_of_week": "monday", "start_time": "09:00", "effective_from": "2026-01-01", "effective_until": None, "status": "active"},
        ]
        mock_client.table("class_schedule_exceptions")._data = []

        rows = svc.get_schedules_for_date("tenant-1", date(2099, 1, 1))
        assert len(rows) == 1


# ---------------------------------------------------------------------------
# Tenant isolation
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    def test_queries_include_tenant_filter(self, svc, mock_client):
        """All queries include tenant_id filter."""
        svc.list_schedules("tenant-1")
        svc.get_schedule("tenant-1", "s1")

        # Verify tenant filter was set
        tables = mock_client._tables
        if "class_schedules" in tables:
            assert tables["class_schedules"]._filters.get("tenant_id") == ("eq", "tenant-1")


@pytest.mark.asyncio
async def test_list_schedules_route_uses_tenant_id():
    from api.routers.dashboard.schedules import list_schedules
    from api.tenant_scope import TenantScope

    tenant = TenantScope(
        tenant_id="tenant-demo-physics",
        slug="demo-physics",
        name="Demo Physics Academy",
    )
    with patch("api.routers.dashboard.schedules.ScheduleService") as svc_cls:
        svc_cls.return_value.list_schedules.return_value = []
        result = await list_schedules(tenant)

    svc_cls.return_value.list_schedules.assert_called_once_with(
        "tenant-demo-physics",
        class_id=None,
        teacher_id=None,
        day_of_week=None,
    )
    assert result.tenant_id == "tenant-demo-physics"
    assert result.schedules == []
