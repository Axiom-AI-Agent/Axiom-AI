#!/usr/bin/env python3
"""Ingest tutor markdown notes into Qdrant for one tenant."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from services.ingest_service.pipeline import run_tenant_ingest

TENANT_SLUGS = {
    "tenant-demo-physics": "demo-physics",
    "tenant-demo-chemistry": "demo-chemistry",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest tutor notes into Qdrant")
    parser.add_argument("--tenant-id", required=True, help="Tenant UUID, e.g. tenant-demo-physics")
    parser.add_argument("--path", default=None, help="Override KB path (default: data/knowledge_base/{slug})")
    parser.add_argument(
        "--strategy",
        choices=("parent_child", "fixed"),
        default="parent_child",
        help="Chunking strategy (default: parent_child)",
    )
    args = parser.parse_args()

    slug = TENANT_SLUGS.get(args.tenant_id, args.tenant_id.replace("tenant-", "").replace("_", "-"))
    kb_path = Path(args.path) if args.path else None

    try:
        n = run_tenant_ingest(
            tenant_id=args.tenant_id,
            tenant_slug=slug,
            kb_path=kb_path,
            strategy=args.strategy,
        )
        print(f"OK: ingested {n} chunks for {args.tenant_id}")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
