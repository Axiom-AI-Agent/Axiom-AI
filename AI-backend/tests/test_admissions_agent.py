"""Admissions agent node tests (in-process CRM, no MCP subprocess)."""

from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage

from agents.nodes.admissions_agent import AdmissionsAgent
from services.admissions.field_definitions import DEFAULT_FIELD_DEFINITIONS
from services.admissions.onboarding_session_store import get_onboarding_session_store


@pytest.fixture(autouse=True)
def clear_onboarding_sessions():
    store = get_onboarding_session_store()
    store._sessions.clear()
    yield
    store._sessions.clear()


class FakeCrmClient:
    def __init__(self) -> None:
        self.student = None
        self.enrollments: list = []
        self.pending_enrollment = None
        self.open_escalation = None
        self.classes = [
            {
                "id": "class-physics-al-2026",
                "subject": "Physics",
                "grade": "A/L",
                "name": "A/L Physics 2026",
                "fee_amount": 5000,
            }
        ]
        self.committed = False
        self.commit_kwargs: dict | None = None
        self.field_definitions = [
            {
                "field_key": defn.field_key,
                "label": defn.label,
                "field_type": defn.field_type,
                "required": defn.required,
                "sort_order": defn.sort_order,
                "active": True,
            }
            for defn in DEFAULT_FIELD_DEFINITIONS
        ]

    async def list_field_definitions(self, *, tenant_id: str) -> list:
        return list(self.field_definitions)

    async def get_student(self, *, tenant_id: str, phone: str) -> dict:
        if self.student is None:
            return {
                "ok": True,
                "student": None,
                "enrollments": [],
                "pending_enrollment": None,
                "open_escalation": None,
            }
        return {
            "ok": True,
            "student": self.student,
            "enrollments": self.enrollments,
            "pending_enrollment": self.pending_enrollment,
            "open_escalation": self.open_escalation,
        }

    async def list_classes(self, *, tenant_id: str, **kwargs) -> list:
        return self.classes

    async def commit_onboarding(self, **kwargs) -> dict:
        self.committed = True
        self.commit_kwargs = kwargs
        self.student = {
            "id": "stu-new",
            "tenant_id": kwargs["tenant_id"],
            "phone": kwargs["phone"],
            "name": kwargs["name"],
            "school": kwargs.get("school"),
            "district": kwargs.get("district"),
            "extra_fields": kwargs.get("extra_fields") or {},
            "consent_at": "2026-01-01T00:00:00+00:00",
        }
        self.pending_enrollment = {
            "id": "enr-1",
            "class_id": kwargs["class_id"],
            "status": "pending",
        }
        return {
            "ok": True,
            "student": self.student,
            "enrollment": self.pending_enrollment,
            "class": self.classes[0],
            "status": "pending",
        }

    async def register_student(self, **kwargs) -> dict:
        raise AssertionError("register_student should not be called during in-memory onboarding")

    async def create_enrollment(self, **kwargs) -> dict:
        raise AssertionError("create_enrollment should not be called directly during onboarding")

    async def create_escalation(self, **kwargs) -> dict:
        self.open_escalation = {"id": "esc-1", "status": "open", "reason_code": kwargs.get("reason_code")}
        return {"ok": True, "escalation": self.open_escalation}


def _state(*, message: str, phone: str = "94771111001") -> dict:
    return {
        "tenant_id": "tenant-demo-physics",
        "tenant_name": "Demo Physics Academy",
        "user_id": "",
        "phone": phone,
        "messages": [HumanMessage(content=message)],
    }


@pytest.mark.asyncio
async def test_admissions_agent_greeting_does_not_start_onboarding():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(_state(message="hi"))
    assert get_onboarding_session_store().get(
        tenant_id="tenant-demo-physics", phone="94771111001"
    ) is None
    assert "full name" not in result.answer.lower()
    assert "register" in result.answer.lower() or "enroll" in result.answer.lower()


@pytest.mark.asyncio
async def test_admissions_agent_who_are_you_does_not_collect_name():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(_state(message="hello who are you"))
    assert get_onboarding_session_store().get(
        tenant_id="tenant-demo-physics", phone="94771111001"
    ) is None
    assert "school" not in result.answer.lower()
    assert "full name" not in result.answer.lower()


@pytest.mark.asyncio
async def test_admissions_agent_prompts_for_name_on_enrollment_intent():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(_state(message="I want to join A/L Physics"))
    assert "name" in result.answer.lower()
    assert not crm.committed


@pytest.mark.asyncio
async def test_admissions_agent_unenrolled_existing_student_starts_collection():
    crm = FakeCrmClient()
    crm.student = {
        "id": "stu-stub",
        "tenant_id": "tenant-demo-physics",
        "phone": "94771111001",
        "name": "Mirco",
        "school": None,
        "district": None,
    }
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(_state(message="I want to join a class"))
    assert "name" in result.answer.lower()
    assert "already registered" not in result.answer.lower()
    assert not crm.committed


@pytest.mark.asyncio
async def test_admissions_agent_shows_review_before_db_write():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    store.start(tenant_id="tenant-demo-physics", phone="94771111001")
    session = store.get(tenant_id="tenant-demo-physics", phone="94771111001")
    assert session is not None
    session.slots.name = "Kavindu Fernando"
    session.slots.school = "Royal College Colombo"
    session.slots.district = "Colombo"
    session.slots.class_id = "class-physics-al-2026"
    session.next_step = "class"
    store.save(tenant_id="tenant-demo-physics", phone="94771111001", session=session)

    result = await agent.run(_state(message="A/L Physics"))
    assert "review" in result.answer.lower() or "confirm" in result.answer.lower()
    assert not crm.committed


@pytest.mark.asyncio
async def test_admissions_agent_commits_only_after_yes():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    session = store.start(tenant_id="tenant-demo-physics", phone="94771111001")
    session.slots.name = "Kavindu Fernando"
    session.slots.school = "Royal College Colombo"
    session.slots.district = "Colombo"
    session.slots.class_id = "class-physics-al-2026"
    session.awaiting_confirmation = True
    session.next_step = "confirm"
    store.save(tenant_id="tenant-demo-physics", phone="94771111001", session=session)

    result = await agent.run(_state(message="YES"))
    assert crm.committed is True
    assert "welcome" in result.answer.lower() or "enrollment" in result.answer.lower()
    assert "successfully enrolled" not in result.answer.lower()
    assert crm.pending_enrollment is not None
    assert crm.pending_enrollment["status"] == "pending"


@pytest.mark.asyncio
async def test_admissions_agent_reject_confirmation_restarts_collection():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    session = store.start(tenant_id="tenant-demo-physics", phone="94771111001")
    session.slots.name = "Kavindu Fernando"
    session.slots.school = "Royal College Colombo"
    session.slots.district = "Colombo"
    session.slots.class_id = "class-physics-al-2026"
    session.awaiting_confirmation = True
    session.next_step = "confirm"
    store.save(tenant_id="tenant-demo-physics", phone="94771111001", session=session)

    result = await agent.run(_state(message="no I need to change the number"))
    assert crm.committed is False
    assert "no problem" in result.answer.lower()
    assert "start over" in result.answer.lower()
    assert "welcome to" not in result.answer.lower()
    session = store.get(tenant_id="tenant-demo-physics", phone="94771111001")
    assert session is not None
    assert session.active is True
    assert session.awaiting_confirmation is False
    assert session.next_step == "name"
    assert session.slots.name is None
    assert session.slots.school is None
    assert session.slots.district is None
    assert session.slots.class_id is None


@pytest.mark.asyncio
async def test_admissions_agent_name_reply_advances_to_school():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    store.start(tenant_id="tenant-demo-physics", phone="94771111001")

    result = await agent.run(_state(message="My name is Mirco Fernando"))
    assert "school" in result.answer.lower()
    session = store.get(tenant_id="tenant-demo-physics", phone="94771111001")
    assert session is not None
    assert session.slots.name == "Mirco Fernando"
    assert not crm.committed


@pytest.mark.asyncio
async def test_admissions_agent_lists_classes_when_asked():
    crm = FakeCrmClient()
    crm.classes = [
        {
            "id": "class-physics-al-2026",
            "subject": "Physics",
            "grade": "A/L",
            "name": "A/L Physics 2026",
            "fee_amount": 5000,
        },
        {
            "id": "class-physics-ol-2026",
            "subject": "Physics",
            "grade": "O/L",
            "name": "O/L Physics 2026",
            "fee_amount": 3500,
        },
    ]
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    session = store.start(tenant_id="tenant-demo-physics", phone="94771111001")
    session.slots.name = "Mirco Fernando"
    session.slots.school = "St John Paul II"
    session.slots.district = "Western Province"
    session.next_step = "class"
    store.save(tenant_id="tenant-demo-physics", phone="94771111001", session=session)

    result = await agent.run(_state(message="what are all the available classes"))
    assert "A/L Physics 2026" in result.answer
    assert "O/L Physics 2026" in result.answer
    assert "Which class would you like to join" not in result.answer


@pytest.mark.asyncio
async def test_admissions_agent_confirm_yes_does_not_relist_classes():
    crm = FakeCrmClient()
    crm.classes = [
        {
            "id": "class-physics-al-2026",
            "subject": "Physics",
            "grade": "A/L",
            "name": "A/L Physics 2026",
            "fee_amount": 5000,
        },
        {
            "id": "class-physics-ol-2026",
            "subject": "Physics",
            "grade": "O/L",
            "name": "O/L Physics 2026",
            "fee_amount": 3500,
        },
    ]
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    session = store.start(tenant_id="tenant-demo-physics", phone="94771111001")
    session.slots.name = "Mirco Fernando"
    session.slots.school = "St.John Paul II"
    session.slots.district = "Western Province"
    session.slots.class_id = "class-physics-al-2026"
    session.awaiting_confirmation = True
    session.next_step = "confirm"
    store.save(tenant_id="tenant-demo-physics", phone="94771111001", session=session)

    result = await agent.run(_state(message="yes"))
    assert "which one would you like" not in result.answer.lower()
    assert crm.committed is True


@pytest.mark.asyncio
async def test_admissions_agent_enrollment_status_for_unknown_visitor():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(_state(message="am i enrolled in a class of your academy"))
    assert "not" in result.answer.lower() and "registered" in result.answer.lower()
    assert get_onboarding_session_store().get(
        tenant_id="tenant-demo-physics", phone="94771111001"
    ) is None


@pytest.mark.asyncio
async def test_admissions_agent_off_topic_during_onboarding_does_not_corrupt_slots():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    store.start(tenant_id="tenant-demo-physics", phone="94771111001")

    result = await agent.run(_state(message="Explain velocity from the tutor notes"))
    assert "name" in result.answer.lower()
    session = store.get(tenant_id="tenant-demo-physics", phone="94771111001")
    assert session is not None
    assert session.slots.name is None


@pytest.mark.asyncio
async def test_admissions_agent_lists_available_classes_for_info_inquiry():
    crm = FakeCrmClient()
    crm.classes = [
        {
            "id": "class-physics-al-2026",
            "subject": "Physics",
            "grade": "A/L",
            "name": "A/L Physics 2026",
            "fee_amount": 5000,
        },
        {
            "id": "class-physics-ol-2026",
            "subject": "Physics",
            "grade": "O/L",
            "name": "O/L Physics 2026",
            "fee_amount": 3500,
        },
    ]
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(
        _state(message="what are the classes that are available currently")
    )
    assert "A/L Physics 2026" in result.answer
    assert "O/L Physics 2026" in result.answer
    assert "enrolled students only" not in result.answer.lower()


@pytest.mark.asyncio
async def test_admissions_agent_asks_custom_field_instead_of_school():
    crm = FakeCrmClient()
    crm.field_definitions = [
        {
            "field_key": "parent_contact",
            "label": "Parent contact",
            "field_type": "text",
            "required": True,
            "sort_order": 0,
            "active": True,
        }
    ]
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    store.start(tenant_id="tenant-demo-physics", phone="94771111001")

    result = await agent.run(_state(message="My name is Mirco Fernando"))
    assert "parent contact" in result.answer.lower()
    assert "school" not in result.answer.lower()
    session = store.get(tenant_id="tenant-demo-physics", phone="94771111001")
    assert session is not None
    assert session.slots.name == "Mirco Fernando"
    assert session.next_step == "parent_contact"


@pytest.mark.asyncio
async def test_admissions_agent_commits_extra_fields():
    crm = FakeCrmClient()
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    session = store.start(tenant_id="tenant-demo-physics", phone="94771111001")
    session.slots.name = "Kavindu Fernando"
    session.slots.school = "Royal College Colombo"
    session.slots.district = "Colombo"
    session.slots.extra = {
        "school": "Royal College Colombo",
        "district": "Colombo",
    }
    session.slots.class_id = "class-physics-al-2026"
    session.awaiting_confirmation = True
    session.next_step = "confirm"
    store.save(tenant_id="tenant-demo-physics", phone="94771111001", session=session)

    result = await agent.run(_state(message="YES"))
    assert crm.committed is True
    assert crm.commit_kwargs is not None
    assert crm.commit_kwargs["extra_fields"]["school"] == "Royal College Colombo"
    assert crm.commit_kwargs["extra_fields"]["district"] == "Colombo"
    assert "welcome" in result.answer.lower() or "enrollment" in result.answer.lower()


@pytest.mark.asyncio
async def test_admissions_agent_reprompts_invalid_select():
    crm = FakeCrmClient()
    crm.field_definitions = [
        {
            "field_key": "stream",
            "label": "Stream",
            "field_type": "select",
            "options": ["Physical", "Biological"],
            "required": True,
            "sort_order": 0,
            "active": True,
        }
    ]
    agent = AdmissionsAgent(crm=crm)
    store = get_onboarding_session_store()
    session = store.start(tenant_id="tenant-demo-physics", phone="94771111001")
    session.slots.name = "Mirco Fernando"
    session.next_step = "stream"
    store.save(tenant_id="tenant-demo-physics", phone="94771111001", session=session)

    result = await agent.run(_state(message="Commerce"))
    assert "please choose one of these" in result.answer.lower()
    assert "physical" in result.answer.lower()
    session = store.get(tenant_id="tenant-demo-physics", phone="94771111001")
    assert session is not None
    assert session.next_step == "stream"
    assert "stream" not in session.slots.extra
    assert not crm.committed
