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
    "tenant_field_definition",
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


def test_students_extra_fields_defaults_to_empty_object(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, column_default, is_nullable, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'students'
              AND column_name = 'extra_fields'
            """
        )
        row = cur.fetchone()
        cur.execute(
            """
            SELECT COUNT(*) FILTER (WHERE extra_fields IS NULL) AS null_count,
                   COUNT(*) FILTER (WHERE extra_fields = '{}'::jsonb) AS empty_count,
                   COUNT(*) AS total
            FROM students
            """
        )
        counts = cur.fetchone()

    assert row is not None, "students.extra_fields column is missing"
    column_name, column_default, is_nullable, data_type = row
    assert column_name == "extra_fields"
    assert is_nullable == "NO"
    assert data_type == "jsonb"
    assert column_default is not None
    assert "'{}'" in column_default.replace(" ", "") or column_default.replace(" ", "").find("{}") >= 0

    _null_count, empty_count, total = counts
    assert _null_count == 0
    if total:
        assert empty_count == total


def test_students_keep_school_and_district_columns(db_conn):
    """school and district stay real columns; extra_fields is additive only."""
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'students'
              AND column_name IN ('school', 'district', 'extra_fields')
            """
        )
        names = {row[0] for row in cur.fetchall()}

    assert names == {"school", "district", "extra_fields"}


def test_every_tenant_has_school_and_district_field_definitions(db_conn):
    """Demo tenants keep today's school/district extras; core fields stay out."""
    with db_conn.cursor() as cur:
        cur.execute("SELECT id FROM tenants WHERE slug LIKE 'demo-%'")
        tenant_ids = [row[0] for row in cur.fetchall()]
        cur.execute(
            """
            SELECT tenant_id, field_key, label, field_type, required, sort_order, active
            FROM tenant_field_definition
            ORDER BY tenant_id, sort_order, field_key
            """
        )
        rows = cur.fetchall()

    assert tenant_ids, "expected at least one tenant"

    by_tenant: dict[str, dict[str, tuple]] = {}
    for tenant_id, field_key, label, field_type, required, sort_order, active in rows:
        by_tenant.setdefault(tenant_id, {})[field_key] = (
            label,
            field_type,
            required,
            sort_order,
            active,
        )

    missing = [tid for tid in tenant_ids if tid not in by_tenant]
    assert not missing, f"tenants missing field definitions: {missing}"

    for tenant_id in tenant_ids:
        keys = by_tenant[tenant_id]
        assert "school" in keys, f"{tenant_id} missing school definition"
        assert "district" in keys, f"{tenant_id} missing district definition"
        assert "name" not in keys
        assert "class" not in keys
        assert "consent" not in keys

        school = keys["school"]
        district = keys["district"]
        assert school == ("School", "text", True, 0, True)
        assert district == ("District", "text", True, 1, True)
        assert school[3] < district[3]


def test_seeded_tenants_have_field_config_locked(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name, is_nullable, data_type, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'tenants'
              AND column_name = 'field_config_locked'
            """
        )
        column = cur.fetchone()
        cur.execute(
            """
            SELECT COUNT(*) FILTER (WHERE field_config_locked IS NOT TRUE)
            FROM tenants
            WHERE EXISTS (
                SELECT 1 FROM tenant_field_definition d
                WHERE d.tenant_id = tenants.id
            )
            """
        )
        unlocked = cur.fetchone()[0]

    assert column is not None, "tenants.field_config_locked column is missing"
    assert column[1] == "NO"
    assert column[2] == "boolean"
    assert unlocked == 0
