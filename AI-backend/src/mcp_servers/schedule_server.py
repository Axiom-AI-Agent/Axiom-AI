"""
Schedule MCP Server — exposes class timetable lookup tools.

Provides get_next_class, get_schedule_for_date, and get_week_schedule
via MCP stdio for the agent pipeline.
"""

from __future__ import annotations

import os
import sys

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from mcp.server.fastmcp import FastMCP

from services.schedule.schedule_service import ScheduleService

mcp = FastMCP("axiom-schedule")
_svc: ScheduleService | None = None


def _init() -> ScheduleService:
    global _svc
    if _svc is None:
        logger.info("Initialising schedule MCP server...")
        _svc = ScheduleService()
    return _svc


@mcp.tool()
def get_next_class(
    tenant_id: str,
    student_id: str = "",
) -> str:
    """Get the next upcoming class for a student. Returns the next scheduled class with day, time, room, and teacher."""
    import json

    svc = _init()
    row = svc.get_next_class(tenant_id, student_id=student_id or None)
    if not row:
        return json.dumps({"ok": True, "found": False, "message": "No upcoming classes found."})
    return json.dumps({"ok": True, "found": True, "schedule": row})


@mcp.tool()
def get_schedule_for_date(
    tenant_id: str,
    date: str,
    student_id: str = "",
) -> str:
    """Get all classes scheduled for a specific date (YYYY-MM-DD). Returns list of classes with times, rooms, and teachers."""
    import json
    from datetime import date as dt_date

    svc = _init()
    try:
        d = dt_date.fromisoformat(date)
    except ValueError:
        return json.dumps({"ok": False, "error": f"Invalid date format: {date}. Use YYYY-MM-DD."})
    rows = svc.get_schedules_for_date(tenant_id, d, student_id=student_id or None)
    return json.dumps({"ok": True, "date": date, "schedules": rows, "count": len(rows)})


@mcp.tool()
def get_week_schedule(
    tenant_id: str,
    student_id: str = "",
) -> str:
    """Get the full weekly schedule. Returns all classes grouped by day with times, rooms, and teachers."""
    import json

    svc = _init()
    rows = svc.get_week_schedule(tenant_id, student_id=student_id or None)
    return json.dumps({"ok": True, "schedules": rows, "count": len(rows)})


if __name__ == "__main__":
    logger.info("Starting axiom-schedule MCP server on stdio...")
    mcp.run()
