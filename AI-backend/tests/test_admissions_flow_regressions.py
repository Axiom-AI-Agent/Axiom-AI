"""End-to-end admissions regressions from the student-side QA log.

Category B is the sticky-flow family: a student with a pending application got
the same "send your payment slip" reply no matter what they asked. Category C1
is registration validation. Each test states the ground truth in the fake CRM
and asserts the agent answers against it rather than replaying the flow.
"""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.admissions_agent import AdmissionsAgent
from services.admissions.onboarding_session_store import get_onboarding_session_store
from tests.test_admissions_agent import FakeCrmClient

PHONE = "94771111001"
TENANT = "tenant-demo-physics"

PHYSICS_AL = {
    "id": "class-physics-al-2026",
    "subject": "Physics",
    "grade": "A/L",
    "name": "A/L Physics 2026",
    "fee_amount": 5000,
}
CHEMISTRY_AL = {
    "id": "class-chem-al-2026",
    "subject": "Chemistry",
    "grade": "A/L",
    "name": "A/L Chemistry 2026",
    "fee_amount": 4500,
}


@pytest.fixture(autouse=True)
def clear_sessions():
    store = get_onboarding_session_store()
    store._sessions.clear()
    yield
    store._sessions.clear()


def _state(message: str) -> dict:
    return {
        "tenant_id": TENANT,
        "tenant_name": "Demo Physics Academy",
        "user_id": "",
        "phone": PHONE,
        "messages": [HumanMessage(content=message)],
    }


def _student_with_pending_application() -> FakeCrmClient:
    crm = FakeCrmClient()
    crm.classes = [PHYSICS_AL, CHEMISTRY_AL]
    crm.student = {
        "id": "stu-1",
        "tenant_id": TENANT,
        "phone": PHONE,
        "name": "Mirco Fernando",
        "school": "St John Paul II",
        "district": "Puttlam",
        "consent_at": "2026-01-01T00:00:00+00:00",
    }
    crm.pending_enrollment = {
        "id": "enr-1",
        "class_id": PHYSICS_AL["id"],
        "status": "pending",
    }
    return crm


def _enrolled_student() -> FakeCrmClient:
    crm = _student_with_pending_application()
    crm.pending_enrollment = None
    crm.enrollments = [
        {"id": "enr-1", "class_id": PHYSICS_AL["id"], "status": "active"}
    ]
    return crm


def _is_payment_prompt(answer: str) -> bool:
    lowered = answer.lower()
    return "payment slip" in lowered or "bank slip" in lowered


# ── B3: a tutor question during a pending payment gets tutor info ────────────
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    ["Can I get some information on the tutor?", "Who are the team at Demo Physics Academy?"],
)
async def test_b3_tutor_question_is_not_answered_with_the_payment_prompt(message: str):
    crm = _student_with_pending_application()
    crm.list_staff = _staff_stub  # type: ignore[attr-defined]

    result = await AdmissionsAgent(crm=crm).run(_state(message))

    assert not _is_payment_prompt(result.answer)
    assert "Chathura" in result.answer


async def _staff_stub(*, tenant_id: str) -> list[dict]:
    return [{"name": "Chathura Perera", "role": "tutor"}]


# ── B1: asking for a different class browses, it does not repeat the flow ────
@pytest.mark.asyncio
async def test_b1_join_another_class_shows_the_catalogue_with_a_nudge():
    crm = _student_with_pending_application()

    result = await AdmissionsAgent(crm=crm).run(_state("I want to join another class"))

    assert "A/L Chemistry 2026" in result.answer
    # The unfinished application is not dropped — it comes back as a reminder.
    assert "payment slip" in result.answer.lower()
    assert result.answer.strip().endswith("!")


# ── B2: already enrolled in the class being asked about ─────────────────────
@pytest.mark.asyncio
async def test_b2_already_enrolled_is_stated_not_re_sold():
    crm = _enrolled_student()

    result = await AdmissionsAgent(crm=crm).run(
        _state("I want to join the A Level physics class")
    )

    assert "already enrolled" in result.answer.lower()
    assert "A/L Physics 2026" in result.answer
    assert not _is_payment_prompt(result.answer)


@pytest.mark.asyncio
async def test_reapplying_for_the_pending_class_says_it_is_pending():
    crm = _student_with_pending_application()

    result = await AdmissionsAgent(crm=crm).run(
        _state("I want to join the A/L Physics 2026 class")
    )

    assert "already have an application" in result.answer.lower()
    assert "A/L Physics 2026" in result.answer


# ── The payment flow still works when the student is actually talking about it
@pytest.mark.asyncio
async def test_payment_question_during_pending_payment_still_gets_the_prompt():
    crm = _student_with_pending_application()

    result = await AdmissionsAgent(crm=crm).run(_state("how do I send the slip?"))

    assert _is_payment_prompt(result.answer)


# ── C1: registration values must be real ────────────────────────────────────
@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["💅💅💅", "🙂🙂", "!!!", "..."])
async def test_c1_emoji_only_name_is_rejected_and_reprompted(value: str):
    crm = FakeCrmClient()
    store = get_onboarding_session_store()
    store.start(tenant_id=TENANT, phone=PHONE)

    result = await AdmissionsAgent(crm=crm).run(_state(value))

    assert "valid" in result.answer.lower()
    assert "name" in result.answer.lower()
    session = store.get(tenant_id=TENANT, phone=PHONE)
    assert session is not None
    assert session.slots.name is None


@pytest.mark.asyncio
async def test_c1_a_real_name_is_still_accepted():
    crm = FakeCrmClient()
    store = get_onboarding_session_store()
    store.start(tenant_id=TENANT, phone=PHONE)

    result = await AdmissionsAgent(crm=crm).run(_state("Mirco Fernando"))

    assert "school" in result.answer.lower()
    session = store.get(tenant_id=TENANT, phone=PHONE)
    assert session is not None
    assert session.slots.name == "Mirco Fernando"


# ── A1: class list is answered for every phrasing, not just one ─────────────
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message",
    [
        "What classes do you teach?",
        "What classes can I sign up for?",
        "Can you give me a list of the classes available",
    ],
)
async def test_a1_every_phrasing_returns_the_class_list(message: str):
    crm = FakeCrmClient()
    crm.classes = [PHYSICS_AL, CHEMISTRY_AL]

    result = await AdmissionsAgent(crm=crm).run(_state(message))

    assert "A/L Physics 2026" in result.answer
    assert "A/L Chemistry 2026" in result.answer
