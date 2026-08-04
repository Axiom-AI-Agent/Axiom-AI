#!/usr/bin/env python3
"""Smoke test: admissions onboarding via in-process CRM (no server required)."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from langchain_core.messages import HumanMessage

from agents.nodes.admissions_agent import AdmissionsAgent, DirectCrmClient
from services.admissions.onboarding_flow import OnboardingFlow


async def main() -> int:
    print("=== Phase 3 admissions smoke (in-process CRM) ===")

    flow = OnboardingFlow()
    steps_ok = True

    # Slot extraction
    state = flow.load_from_student(None)
    state = flow.apply_message(state, "I want to join A/L Physics")
    if state.next_step != "name":
        print(f"FAIL: expected next_step=name, got {state.next_step}")
        steps_ok = False
    else:
        print("OK: enrollment intent does not capture as name")

    classes = [
        {"id": "class-al", "subject": "Physics", "grade": "A/L", "name": "A/L Physics"},
        {"id": "class-ol", "subject": "Physics", "grade": "O/L", "name": "O/L Physics"},
    ]
    state = flow.apply_message(state, "Kavindu Fernando")
    state = flow.apply_message(state, "Royal College")
    state = flow.apply_message(state, "Colombo")
    state = flow.apply_message(state, "A/L Physics", classes=classes)
    state = flow.apply_message(state, "YES")
    if not state.complete or state.slots.class_id != "class-al":
        print(f"FAIL: onboarding not complete: {state}")
        steps_ok = False
    else:
        print("OK: full slot extraction through consent")

    # Agent first-turn prompt (uses DirectCrmClient — needs Supabase for live student)
    try:
        agent = AdmissionsAgent(crm=DirectCrmClient())
        result = await agent.run(
            {
                "tenant_id": "tenant-demo-physics",
                "tenant_name": "Demo Physics Academy",
                "user_id": "stu-smoke",
                "phone": "94779999001",
                "messages": [HumanMessage(content="Hi, I want to enroll")],
            }
        )
        if "name" not in result.answer.lower():
            print(f"FAIL: agent did not ask for name: {result.answer[:120]}")
            steps_ok = False
        else:
            print("OK: agent asks for name on first turn")
    except Exception as exc:
        print(f"SKIP live agent test (Supabase): {exc}")

    if steps_ok:
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
