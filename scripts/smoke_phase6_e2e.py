#!/usr/bin/env python3
"""
Phase 6 E2E smoke — five scenarios via POST /chat pipeline (no Twilio).

Patterns copied from:
  - ``scripts/smoke_st_memory.py`` (live ChatPipeline + unique phone)
  - BookMe AI ``scripts/test_chat_pipeline.py`` (OOS short-circuit)
  - ``scripts/smoke_admissions.py`` (onboarding turns)

Drive MCP and Twilio are **out of scope** — resource scenario uses RAG phrasing only.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

TENANT_ID = "tenant-demo-physics"
MEDIA_URL = "https://example.com/payment-slip-demo.jpg"


def _phone() -> str:
    return f"9477099{int(time.time()) % 10000:04d}"


def _require_live_env() -> bool:
    if not os.getenv("OPENAI_API_KEY"):
        print("SKIP: OPENAI_API_KEY not set")
        return False
    if not (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_KEY")):
        print("SKIP: SUPABASE_URL / SUPABASE_SERVICE_KEY not set")
        return False
    return True


async def _chat(pipeline, phone: str, body: str, *, media_url: str | None = None) -> str:
    from domain.enums import ChatChannel
    from services.messaging.schemas import InboundMessage

    result = await pipeline.aprocess_message(
        InboundMessage(
            channel=ChatChannel.HTTP_DEV,
            tenant_id=TENANT_ID,
            phone=phone,
            body=body,
            media_url=media_url,
            num_media=1 if media_url else 0,
        )
    )
    print(f"  → {body[:60]!r}")
    print(f"  ← {(result.reply or '')[:160]}")
    return result.reply or ""


async def scenario_onboarding(pipeline, phone: str) -> bool:
    print("\n[1/5] Onboarding")
    await _chat(pipeline, phone, "Hi, I want to enroll in A/L Physics")
    await _chat(pipeline, phone, "Kavindu Perera")
    await _chat(pipeline, phone, "Royal College")
    await _chat(pipeline, phone, "Colombo")
    reply = await _chat(pipeline, phone, "A/L Physics")
    consent = await _chat(pipeline, phone, "YES")
    ok = any(w in (reply + consent).lower() for w in ("consent", "payment", "enroll", "pending", "class"))
    print("OK onboarding" if ok else "FAIL onboarding: unexpected replies")
    return ok


async def scenario_resource_rag(pipeline, phone: str) -> bool:
    print("\n[2/5] Resource (RAG — no Drive MCP)")
    reply = await _chat(
        pipeline,
        phone,
        "Can you explain velocity from the tutor notes you have uploaded?",
    )
    ok = len(reply.strip()) > 20
    print("OK resource/rag" if ok else "FAIL resource: empty reply")
    return ok


async def scenario_payment(pipeline, phone: str) -> bool:
    print("\n[3/5] Payment receipt")
    await scenario_onboarding(pipeline, phone)
    reply = await _chat(
        pipeline,
        phone,
        "Here is my bank slip",
        media_url=MEDIA_URL,
    )
    ok = any(w in reply.lower() for w in ("verify", "team", "payment", "thank", "received"))
    print("OK payment ack" if ok else "FAIL payment: no verification ack")
    return ok


async def scenario_escalation(pipeline, phone: str) -> bool:
    print("\n[4/5] Talk to tutor")
    reply = await _chat(pipeline, phone, "Can I speak to sir please? I need to talk to my tutor.")
    ok = any(w in reply.lower() for w in ("tutor", "notify", "team", "contact"))
    print("OK escalation ack" if ok else "FAIL escalation: no tutor ack")
    return ok


async def scenario_out_of_scope() -> bool:
    print("\n[5/5] Off-topic (decision graph only — BookMe test_chat_pipeline pattern)")
    from agents.chat_pipeline import run_chat_turn
    from agents.runtime import get_decision_graph, get_orchestrator
    from services.identity.context import IdentityContext

    ctx = IdentityContext(
        tenant_id=TENANT_ID,
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        student_id="stu-smoke-oos",
        phone="94779999002",
        session_id=f"{TENANT_ID}:94779999002",
    )
    result = await run_chat_turn(
        ctx=ctx,
        message="What's the weather in Colombo today?",
        decision_graph=get_decision_graph(),
        orchestrator=await get_orchestrator(),
        channel="http_dev",
    )
    print(f"  verdict={result.verdict} route={result.route}")
    print(f"  ← {(result.answer or '')[:160]}")
    ok = result.verdict == "out_of_scope" and bool(result.answer)
    print("OK out_of_scope" if ok else "FAIL out_of_scope")
    return ok


async def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 6 E2E smoke")
    parser.add_argument(
        "--scenario",
        choices=("all", "onboarding", "resource", "payment", "escalation", "oos"),
        default="all",
    )
    args = parser.parse_args()

    if not _require_live_env():
        return 0

    from agents.runtime import configure_agent_runtime
    from services.messaging.pipeline import ChatPipeline

    use_mcp = os.getenv("AGENT_USE_MCP", "false").lower() == "true"
    configure_agent_runtime(use_mcp=use_mcp)
    pipeline = ChatPipeline()

    print("=== Phase 6 E2E smoke ===")
    print(f"Tenant: {TENANT_ID} | MCP={use_mcp} | Drive MCP excluded")

    results: list[bool] = []
    phone = _phone()

    if args.scenario in ("all", "onboarding"):
        results.append(await scenario_onboarding(pipeline, _phone()))
    if args.scenario in ("all", "resource"):
        results.append(await scenario_resource_rag(pipeline, _phone()))
    if args.scenario in ("all", "payment"):
        results.append(await scenario_payment(pipeline, _phone()))
    if args.scenario in ("all", "escalation"):
        results.append(await scenario_escalation(pipeline, _phone()))
    if args.scenario in ("all", "oos"):
        results.append(await scenario_out_of_scope())

    if results and all(results):
        print("\n=== Phase 6 e2e passed ===")
        return 0
    print("\n=== Phase 6 e2e FAILED ===")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
