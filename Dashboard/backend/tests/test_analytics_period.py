from datetime import datetime, timezone

import pytest

from app.services.dashboard_service import analytics_start_date


def test_analytics_start_date_today():
    start = analytics_start_date("today")
    now = datetime.now(timezone.utc)
    assert start.hour == 0
    assert start.minute == 0
    assert start.date() == now.date()


def test_analytics_start_date_7d():
    start = analytics_start_date("7d")
    now = datetime.now(timezone.utc)
    delta = now - start
    assert 6.9 <= delta.total_seconds() / 86400 <= 7.1


def test_analytics_start_date_month():
    start = analytics_start_date("month")
    now = datetime.now(timezone.utc)
    assert start.day == 1
    assert start.month == now.month
    assert start.year == now.year


def test_analytics_start_date_48h():
    start = analytics_start_date("48h")
    now = datetime.now(timezone.utc)
    delta = now - start
    assert 47.9 <= delta.total_seconds() / 3600 <= 48.1


def test_analytics_start_date_30d():
    start = analytics_start_date("30d")
    now = datetime.now(timezone.utc)
    delta = now - start
    assert 29.9 <= delta.total_seconds() / 86400 <= 30.1


def test_analytics_start_date_90d():
    start = analytics_start_date("90d")
    now = datetime.now(timezone.utc)
    delta = now - start
    assert 89.9 <= delta.total_seconds() / 86400 <= 90.1


def test_analytics_start_date_rejects_unknown():
    with pytest.raises(ValueError):
        analytics_start_date("year")
