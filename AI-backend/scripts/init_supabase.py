#!/usr/bin/env python3
"""
Apply SQL migrations to Supabase via PostgREST rpc or direct SQL.

Requires SUPABASE_DB_URL (postgres connection string) for DDL.
If only REST keys are available, run sql/01_schema.sql in Supabase SQL editor manually.

Usage:
    PYTHONPATH=src python scripts/init_supabase.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = PROJECT_ROOT / "sql"


def _run_via_psycopg(db_url: str) -> None:
    try:
        import psycopg
    except ImportError:
        print("Install psycopg: pip install 'psycopg[binary]'")
        sys.exit(1)

    files = sorted(SQL_DIR.glob("*.sql"))
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            for path in files:
                print(f"Applying {path.name}...")
                cur.execute(path.read_text(encoding="utf-8"))
                conn.commit()
    print("Schema applied successfully.")


def main() -> None:
    db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")
    if not db_url:
        print(
            "Set SUPABASE_DB_URL to your Postgres connection string, or run "
            "sql/01_schema.sql and sql/02_seed_demo.sql in the Supabase SQL editor."
        )
        sys.exit(1)
    _run_via_psycopg(db_url)


if __name__ == "__main__":
    main()
