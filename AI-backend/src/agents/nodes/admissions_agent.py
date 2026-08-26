"""Admissions agent node — multi-turn onboarding via CRM MCP tools."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage
from loguru import logger

from agents.nodes.crm_client import CrmClient, DirectCrmClient
from agents.state import AgentState
from services.admissions.institute_info import (
    classify_info_inquiry,
    extract_class_filters,
    format_class_details,
    format_staff_list,
    format_tenant_info,
    looks_like_institute_info,
)
from services.admissions.onboarding_flow import OnboardingFlow
from services.admissions.onboarding_session_store import (
    OnboardingSession,
    get_onboarding_session_store,
)


@dataclass
class AdmissionsAgentResult:
    answer: str
    tool_output: str = ""


class AdmissionsAgent:
    def __init__(
        self,
        *,
        crm: CrmClient | None = None,
        flow: OnboardingFlow | None = None,
    ) -> None:
        self.crm = crm or DirectCrmClient()
        self.flow = flow or OnboardingFlow()
        self.session_store = get_onboarding_session_store()

    async def run(self, state: AgentState) -> AdmissionsAgentResult:
        tenant_id = state.get("tenant_id") or ""
        tenant_name = state.get("tenant_name") or "our tuition centre"
        phone = state.get("phone") or ""
        user_message = _last_user_text(state)
        tool_log: list[str] = []

        if not tenant_id or not phone:
            return AdmissionsAgentResult(
                answer="I need your contact details to complete registration. Please try again.",
            )

        if looks_like_institute_info(user_message):
            return await self._handle_info_inquiry(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                user_message=user_message,
                tool_log=tool_log,
            )

        student_payload = await self.crm.get_student(tenant_id=tenant_id, phone=phone)
        tool_log.append(f"get_student: {json.dumps(student_payload)[:300]}")
        student = student_payload.get("student")

        if student:
            return await self._handle_existing_student(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                phone=phone,
                student=student,
                student_payload=student_payload,
                user_message=user_message,
                tool_log=tool_log,
            )

        return await self._handle_new_student_onboarding(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            phone=phone,
            user_message=user_message,
            tool_log=tool_log,
        )

    async def _handle_existing_student(
        self,
        *,
        tenant_id: str,
        tenant_name: str,
        phone: str,
        student: dict[str, Any],
        student_payload: dict[str, Any],
        user_message: str,
        tool_log: list[str],
    ) -> AdmissionsAgentResult:
        enrollments = student_payload.get("enrollments") or []
        pending_enrollment = student_payload.get("pending_enrollment")
        open_escalation = student_payload.get("open_escalation")

        ob_state = self.flow.load_from_student(
            student,
            enrollments=enrollments,
            pending_enrollment=pending_enrollment,
            open_escalation=open_escalation,
        )

        if ob_state.already_enrolled and ob_state.complete:
            class_row = await self._class_for_enrollment(tenant_id, ob_state.slots.class_id)
            answer = self.flow.already_registered_message(
                student=student,
                class_row=class_row,
                tenant_name=tenant_name,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        if ob_state.awaiting_review:
            answer = self.flow.awaiting_review_message(tenant_name=tenant_name)
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        if ob_state.pending_payment:
            answer = self.flow.payment_pending_message(
                slots=ob_state.slots,
                class_row=await self._class_for_enrollment(
                    tenant_id, ob_state.slots.class_id
                ),
                tenant_name=tenant_name,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        # Known phone, no class yet — collect enrollment like a new student.
        return await self._handle_new_student_onboarding(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            phone=phone,
            user_message=user_message,
            tool_log=tool_log,
        )

    async def _handle_info_inquiry(
        self,
        *,
        tenant_id: str,
        tenant_name: str,
        user_message: str,
        tool_log: list[str],
    ) -> AdmissionsAgentResult:
        kind = classify_info_inquiry(user_message) or "classes"

        if kind == "staff":
            staff = await self.crm.list_staff(tenant_id=tenant_id)
            tool_log.append(f"list_staff: {len(staff)} members")
            answer = format_staff_list(staff=staff, tenant_name=tenant_name)
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        if kind == "tenant":
            payload = await self.crm.get_tenant_info(tenant_id=tenant_id)
            tool_log.append(f"get_tenant_info: ok={payload.get('ok')}")
            if not payload.get("ok"):
                answer = (
                    f"I couldn't load centre details for {tenant_name} right now. "
                    f"Please try again or contact the office on WhatsApp."
                )
                return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))
            answer = format_tenant_info(
                tenant=payload.get("tenant") or {"name": tenant_name},
                classes=payload.get("classes") or [],
                staff=payload.get("staff") or [],
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        subject, grade = extract_class_filters(user_message)
        if kind == "class_detail":
            payload = await self.crm.get_class_details(
                tenant_id=tenant_id,
                subject=subject,
                grade=grade,
            )
            tool_log.append(
                f"get_class_details: subject={subject}, grade={grade}, "
                f"count={len(payload.get('classes') or [])}"
            )
            classes = payload.get("classes") or []
            answer = format_class_details(
                classes=classes,
                tenant_name=tenant_name,
                subject=subject,
                grade=grade,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        classes = await self.crm.list_classes(
            tenant_id=tenant_id,
            subject=subject,
            grade=grade,
        )
        tool_log.append(f"list_classes: {len(classes)} classes")
        answer = self.flow.class_catalog_message(
            classes=classes,
            tenant_name=tenant_name,
            intro=f"Here are the classes currently available at {tenant_name}:",
        )
        return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

    async def _handle_new_student_onboarding(
        self,
        *,
        tenant_id: str,
        tenant_name: str,
        phone: str,
        user_message: str,
        tool_log: list[str],
    ) -> AdmissionsAgentResult:
        session = self.session_store.get(tenant_id=tenant_id, phone=phone)
        if session is None and self.flow._looks_like_enrollment_status_query(user_message):
            return AdmissionsAgentResult(
                answer=self.flow.not_registered_status_message(tenant_name=tenant_name),
                tool_output="\n".join(tool_log),
            )

        if session is None and self.flow._looks_like_enrollment_intent(user_message):
            session = self.session_store.start(tenant_id=tenant_id, phone=phone)
            tool_log.append("onboarding_session: started")

        if session is None or not session.active:
            return AdmissionsAgentResult(
                answer=(
                    f"Thanks for your interest in {tenant_name}! "
                    f"When you're ready to enroll, just say you'd like to join a class."
                ),
                tool_output="\n".join(tool_log),
            )

        ob_state = session.to_state()
        classes = await self.crm.list_classes(tenant_id=tenant_id)
        tool_log.append(f"list_classes: {len(classes)} classes")

        if ob_state.awaiting_confirmation and self.flow._looks_like_confirm(user_message):
            return await self._commit_onboarding(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                phone=phone,
                ob_state=ob_state,
                classes=classes,
                tool_log=tool_log,
            )

        if self.flow._looks_like_off_topic_during_onboarding(user_message):
            answer = self.flow.prompt_for_step(
                ob_state.next_step,
                tenant_name=tenant_name,
                phone=phone,
                student_name=ob_state.slots.name,
                classes=classes if ob_state.next_step == "class" else None,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        ob_state = self.flow.apply_message(
            ob_state,
            user_message,
            classes=classes,
            phone=phone,
        )

        if ob_state.ambiguous_classes:
            session = OnboardingSession.from_state(ob_state)
            self.session_store.save(tenant_id=tenant_id, phone=phone, session=session)
            answer = self.flow.disambiguation_prompt(ob_state.ambiguous_classes)
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        session = OnboardingSession.from_state(ob_state)
        self.session_store.save(tenant_id=tenant_id, phone=phone, session=session)

        if ob_state.awaiting_confirmation:
            class_row = next(
                (c for c in classes if c.get("id") == ob_state.slots.class_id),
                None,
            )
            answer = self.flow.review_confirmation_message(
                slots=ob_state.slots,
                class_row=class_row,
                tenant_name=tenant_name,
                phone=phone,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        if ob_state.complete and ob_state.slots.confirmed:
            return await self._commit_onboarding(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                phone=phone,
                ob_state=ob_state,
                classes=classes,
                tool_log=tool_log,
            )

        if (
            ob_state.next_step == "class"
            and not ob_state.slots.class_id
            and self.flow._looks_like_class_catalog_request(user_message)
        ):
            answer = self.flow.class_catalog_message(
                classes=classes,
                tenant_name=tenant_name,
                student_name=ob_state.slots.name,
                intro="Of course! Here's what we offer:",
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        answer = self.flow.prompt_for_step(
            ob_state.next_step,
            tenant_name=tenant_name,
            phone=phone,
            student_name=ob_state.slots.name,
            classes=classes if ob_state.next_step == "class" else None,
        )
        return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

    async def _commit_onboarding(
        self,
        *,
        tenant_id: str,
        tenant_name: str,
        phone: str,
        ob_state: Any,
        classes: list[dict[str, Any]],
        tool_log: list[str],
    ) -> AdmissionsAgentResult:
        slots = ob_state.slots
        if not (slots.name and slots.school and slots.district and slots.class_id):
            return AdmissionsAgentResult(
                answer="Some enrollment details are missing. Let's start again — what is your full name?",
                tool_output="\n".join(tool_log),
            )

        payload = await self.crm.commit_onboarding(
            tenant_id=tenant_id,
            phone=phone,
            name=slots.name,
            school=slots.school,
            district=slots.district,
            class_id=slots.class_id,
        )
        tool_log.append(f"commit_onboarding: {json.dumps(payload)[:400]}")
        self.session_store.clear(tenant_id=tenant_id, phone=phone)

        if not payload.get("ok"):
            error = payload.get("error", "Could not complete enrollment.")
            return AdmissionsAgentResult(
                answer=f"Sorry — {error} Please try again or contact the office.",
                tool_output="\n".join(tool_log),
            )

        answer = self.flow.enrollment_welcome_message(
            slots=slots,
            class_row=payload.get("class"),
            tenant_name=tenant_name,
        )
        return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

    async def _class_for_enrollment(
        self, tenant_id: str, class_id: str | None
    ) -> dict[str, Any] | None:
        if not class_id:
            return None
        classes = await self.crm.list_classes(tenant_id=tenant_id)
        return next((c for c in classes if c.get("id") == class_id), None)


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if hasattr(msg, "content"):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


async def run_admissions_agent(
    state: AgentState,
    *,
    crm: CrmClient | None = None,
) -> dict[str, Any]:
    agent = AdmissionsAgent(crm=crm)
    result = await agent.run(state)
    logger.debug("Admissions agent tool_output: {}", result.tool_output[:500])
    return {
        "messages": [AIMessage(content=result.answer)],
        "agent_outputs": [
            {
                "route": "admissions",
                "tool_output": result.tool_output,
                "answer": result.answer,
                "status": "ok",
            }
        ],
    }


from agents.nodes.crm_client import DirectCrmClient, McpCrmClient

__all__ = ["DirectCrmClient", "McpCrmClient", "AdmissionsAgent", "run_admissions_agent"]
