#!/usr/bin/env python3
"""Phase 0 acceptance gate — run after `make run` or standalone (pytest only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=True)


def run_pytest() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "src"},
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr


def check_live(base_url: str) -> dict[str, object]:
    try:
        import httpx
    except ImportError:
        return {"skipped": True, "reason": "httpx not installed"}

    out: dict[str, object] = {}
    with httpx.Client(base_url=base_url, timeout=5.0) as client:
        health = client.get("/health")
        out["health_status"] = health.status_code
        out["health_body"] = health.json()
        out["health_headers"] = {
            "X-Request-ID": health.headers.get("x-request-id"),
            "X-Response-Time-Ms": health.headers.get("x-response-time-ms"),
        }

        ready = client.get("/ready")
        out["ready_status"] = ready.status_code
        out["ready_body"] = ready.json()

        config = client.get("/config")
        out["config_status"] = config.status_code
        out["config_body"] = config.json()
    return out


def main() -> None:
    print("=== Phase 0 Verification ===\n")

    ok, pytest_out = run_pytest()
    print("[pytest]", "PASS" if ok else "FAIL")
    if not ok:
        print(pytest_out)
    else:
        last_line = [ln for ln in pytest_out.strip().splitlines() if "passed" in ln]
        print(" ", last_line[-1] if last_line else pytest_out.strip())

    base = os.getenv("PHASE0_BASE_URL", "http://127.0.0.1:8000")
    live = check_live(base)
    if live.get("skipped"):
        print("\n[live API] SKIP —", live.get("reason"))
    else:
        print(f"\n[live API] {base}")
        health_ok = live.get("health_status") == 200 and live["health_body"].get("status") == "ok"
        print("  /health     ", "PASS" if health_ok else "FAIL", json.dumps(live["health_body"]))
        print("  headers     ", live.get("health_headers"))
        ready_body = live.get("ready_body", {})
        ready_ok = ready_body.get("ready") is True
        print("  /ready      ", "PASS" if ready_ok else "WARN (needs Supabase)", json.dumps(ready_body))
        config_body = live.get("config_body", {})
        config_ok = (
            config_body.get("chat_model") == "gpt-4o-mini"
            and config_body.get("merge_model") == "gemini-2.0-flash"
        )
        print("  /config     ", "PASS" if config_ok else "FAIL", json.dumps(config_body))

    supabase = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY"))
    langfuse = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
    llm = any(os.getenv(k) for k in ("OPENAI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY"))

    print("\n[env]")
    print("  .env file   ", "found" if (ROOT / ".env").exists() else "missing — copy .env.example")
    print("  Supabase    ", "configured" if supabase else "not set → /ready stays false")
    print("  Langfuse    ", "configured" if langfuse else "optional for Phase 0")
    print("  LLM keys    ", "configured" if llm else "not set → smoke-llm skips")

    print("\n=== Gate summary ===")
    blockers = []
    if not ok:
        blockers.append("pytest failing")
    if not supabase:
        blockers.append("Supabase not configured (apply sql/ + set SUPABASE_* in .env)")
    if blockers:
        print("NOT READY for Phase 1 until:", "; ".join(blockers))
        sys.exit(1)
    print("Core Phase 0 PASS — proceed to Phase 1 when /ready is green")


if __name__ == "__main__":
    main()
