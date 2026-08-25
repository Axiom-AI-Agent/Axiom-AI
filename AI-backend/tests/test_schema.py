"""Validate v2 ER schema tables exist in Supabase when DATABASE_URL is configured."""

from __future__ import annotations

import os

import pytest

EXPECTED_TABLES = (
    "tenants",
    "staff_users",
    "audit_logs",
    "parent_guardians",
    "students",
    "student_channels",
    "subject_classes",
    "enrollments",
    "invoices",
    "bank_slip_uploads",
    "message_logs",
    "escalations",
    "mem_procedures",
    "mem_facts",
    "mem_episodes",
    "st_turns",
)

LEGACY_TABLES = (
    "tenant_integrations",
    "classes",
    "chat_sessions",
    "chat_logs",
    "payments",
    "procedures",
)


def _db_url() -> str | None:
    return os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")


@pytest.fixture(scope="module")
def db_conn():
    url = _db_url()
    if not url:
        pytest.skip("SUPABASE_DB_URL not set — run `make init-db` first")
    psycopg = pytest.importorskip("psycopg")
    try:
        conn = psycopg.connect(url)
    except Exception as exc:
        pytest.skip(f"Database unavailable: {exc}")
    yield conn
    conn.close()


def test_expected_tables_exist(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            """
        )
        names = {row[0] for row in cur.fetchall()}

    missing = [t for t in EXPECTED_TABLES if t not in names]
    assert not missing, f"Missing tables: {missing}"


def test_legacy_tables_removed(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            """
        )
        names = {row[0] for row in cur.fetchall()}

    present = [t for t in LEGACY_TABLES if t in names]
    assert not present, f"Legacy tables still present: {present}"


def test_demo_seed_present(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM tenants WHERE slug LIKE 'demo-%'")
        tenant_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM parent_guardians")
        parent_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM subject_classes")
        class_count = cur.fetchone()[0]

    assert tenant_count >= 2
    assert parent_count >= 2
    assert class_count >= 2
