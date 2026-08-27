"""Admissions agent node — multi-turn onboarding via CRM MCP tools."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage
from loguru import logger

from agents.nodes.crm_client import CrmClient, DirectCrmClient
from agents.state import AgentState
from services.admissions.flow_control import FlowKind, decide_flow_action, flow_kind_for_student
from services.admissions.institute_info import (
    classify_info_inquiry,
    extract_class_filters,
    format_class_details,
    format_staff_list,
    format_tenant_info,
    looks_like_institute_info,
)
from services.admissions.onboarding_flow import OnboardingFlow
from services.admissions.onboarding_route import resume_onboarding_session
from services.admissions.onboarding_session_store import (
    OnboardingSession,
    get_onboarding_session_store,
)
from services.language import normalize_language_pref, t
from services.nlu import IntentResult, StudentIntent, classify
from services.nlu.entities import resolve_class_reference, validate_registration_value

#: Below this the classifier is guessing between neighbouring intents, so the
#: older keyword path gets a say rather than committing to a CRM lookup.
_INFO_CONFIDENCE_FLOOR = 0.45

#: Intents the admissions agent answers directly from CRM ground truth, and the
#: ``classify_info_inquiry`` kind each maps onto.
_INFO_INTENT_KINDS = {
    StudentIntent.CLASS_LIST: "classes",
    StudentIntent.CLASS_DETAIL: "class_detail",
    StudentIntent.TUTOR_INFO: "staff",
    StudentIntent.CENTRE_INFO: "tenant",
}


@dataclass
class AdmissionsAgentResult:
    answer: str
    tool_output: str = ""
    nudge_key: str | None = None

    def with_nudge(self, nudge_key: str | None, language: str) -> AdmissionsAgentResult:
        """Append the unfinished flow's reminder to an interrupting answer."""
        if not nudge_key:
            return self
        return AdmissionsAgentResult(
            answer=f"{self.answer}\n\n{t(nudge_key, language)}",
            tool_output=self.tool_output,
            nudge_key=nudge_key,
        )


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
        self.flow.language = normalize_language_pref(state.get("language_pref"))

        if not tenant_id or not phone:
            return AdmissionsAgentResult(
                answer=t("need_contact_details", self.flow.language),
            )

        await self._load_field_definitions(tenant_id, tool_log)

        intent = state.get("intent") or classify(user_message)
        tool_log.append(f"intent: {intent.intent.value} ({intent.source}, {intent.confidence:.2f})")

        # Mid-onboarding, a bare "A/L Physics" is the answer to "which class?",
        # not a catalogue question. The route-lock upstream has already let
        # genuine topic changes through, so anything reaching here belongs to
        # the collector.
        collecting = self.session_store.is_active(tenant_id=tenant_id, phone=phone)

        if not collecting:
            # An unambiguous info question is answered from CRM ground truth no
            # matter what flow the student is part-way through — this is what
            # used to be swallowed by the pending-payment branch below (B3).
            if intent.intent in _INFO_INTENT_KINDS and intent.confidence >= _INFO_CONFIDENCE_FLOOR:
                return await self._handle_info_inquiry(
                    tenant_id=tenant_id,
                    tenant_name=tenant_name,
                    user_message=user_message,
                    tool_log=tool_log,
                    kind=_INFO_INTENT_KINDS[intent.intent],
                )

            if intent.intent is StudentIntent.UNKNOWN and looks_like_institute_info(user_message):
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
                intent=intent,
                tool_log=tool_log,
            )

        return await self._handle_new_student_onboarding(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            phone=phone,
            user_message=user_message,
            intent=intent,
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
        intent: IntentResult,
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

        flow = flow_kind_for_student(
            onboarding_active=False,
            already_enrolled=bool(ob_state.already_enrolled and ob_state.complete),
            pending_payment=bool(ob_state.pending_payment),
            awaiting_review=bool(ob_state.awaiting_review),
        )
        decision = decide_flow_action(intent, flow=flow, message=user_message)
        tool_log.append(f"flow: {flow.value} → {decision.action.value} ({decision.reason})")

        if intent.intent is StudentIntent.ENROLL:
            return await self._handle_enrollment_request(
                tenant_id=tenant_id,
                tenant_name=tenant_name,
                phone=phone,
                user_message=user_message,
                intent=intent,
                enrollments=enrollments,
                pending_enrollment=pending_enrollment,
                flow=flow,
                tool_log=tool_log,
            )

        if decision.interrupts:
            # Not admissions' subject any more. Say so plainly instead of
            # replaying the flow's next step at the student.
            answer = self.flow._t("onboarding_interest", tenant_name=tenant_name)
            return AdmissionsAgentResult(
                answer=answer, tool_output="\n".join(tool_log)
            ).with_nudge(decision.nudge_key, self.flow.language)

        if flow is FlowKind.NONE and ob_state.already_enrolled and ob_state.complete:
            class_row = await self._class_for_enrollment(tenant_id, ob_state.slots.class_id)
            answer = self.flow.already_registered_message(
                student=student,
                class_row=class_row,
                tenant_name=tenant_name,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        if flow is FlowKind.AWAITING_REVIEW:
            answer = self.flow.awaiting_review_message(tenant_name=tenant_name)
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        if flow is FlowKind.PAYMENT_PENDING:
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
            intent=intent,
            tool_log=tool_log,
        )

    async def _handle_enrollment_request(
        self,
        *,
        tenant_id: str,
        tenant_name: str,
        phone: str,
        user_message: str,
        intent: IntentResult,
        enrollments: list[dict[str, Any]],
        pending_enrollment: dict[str, Any] | None,
        flow: FlowKind,
        tool_log: list[str],
    ) -> AdmissionsAgentResult:
        """Answer "I want to join X" against real enrollment rows (B1, B2).

        Which reply is correct depends entirely on ground truth: already
        enrolled in the named class, already applied for it, or a genuinely new
        class the student can be signed up for.
        """
        classes = await self.crm.list_classes(tenant_id=tenant_id)
        tool_log.append(f"list_classes: {len(classes)} classes")
        reference = resolve_class_reference(user_message, classes=classes)

        target = reference.only_match
        if target is not None:
            target_id = target.get("id")
            active = {
                e.get("class_id")
                for e in enrollments
                if str(e.get("status") or "").lower() in {"active", "approved", "enrolled"}
            }
            label = _class_label(target)
            if target_id in active:
                tool_log.append(f"ground_truth: already enrolled in {target_id}")
                return AdmissionsAgentResult(
                    answer=t(
                        "already_enrolled_in_class",
                        self.flow.language,
                        class_label=label,
                        tenant_name=tenant_name,
                    ),
                    tool_output="\n".join(tool_log),
                )
            if pending_enrollment and pending_enrollment.get("class_id") == target_id:
                tool_log.append(f"ground_truth: application pending for {target_id}")
                return AdmissionsAgentResult(
                    answer=t(
                        "application_already_pending",
                        self.flow.language,
                        class_label=label,
                        tenant_name=tenant_name,
                    ),
                    tool_output="\n".join(tool_log),
                )

        # A different class than the one in flight: show what's on offer rather
        # than repeating the pending application's payment prompt.
        nudge = "nudge_send_payment_slip" if flow is FlowKind.PAYMENT_PENDING else None
        answer = self.flow.class_catalog_message(
            classes=reference.matches or classes,
            tenant_name=tenant_name,
        )
        return AdmissionsAgentResult(
            answer=answer, tool_output="\n".join(tool_log)
        ).with_nudge(nudge, self.flow.language)

    async def _handle_info_inquiry(
        self,
        *,
        tenant_id: str,
        tenant_name: str,
        user_message: str,
        tool_log: list[str],
        kind: str | None = None,
    ) -> AdmissionsAgentResult:
        kind = kind or classify_info_inquiry(user_message) or "classes"

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
        catalogue: list[dict[str, Any]] | None = None
        if subject is None:
            # Typo-tolerant second pass against the tenant's real classes, so
            # "phyiscs clss" still narrows the answer instead of listing all.
            # Only reached when the literal pass found no subject, and the rows
            # it fetches are reused below rather than queried twice.
            catalogue = await self.crm.list_classes(tenant_id=tenant_id)
            tool_log.append(f"list_classes: {len(catalogue)} classes")
            reference = resolve_class_reference(user_message, classes=catalogue)
            subject = reference.subject
            grade = grade or reference.grade
            if reference.corrected_terms:
                tool_log.append(f"typo_correction: {reference.corrected_terms}")

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

        if catalogue is not None and not subject and not grade:
            classes = catalogue
        else:
            classes = await self.crm.list_classes(
                tenant_id=tenant_id,
                subject=subject,
                grade=grade,
            )
            tool_log.append(f"list_classes: {len(classes)} classes")
        answer = self.flow.class_catalog_message(
            classes=classes,
            tenant_name=tenant_name,
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
        intent: IntentResult | None = None,
    ) -> AdmissionsAgentResult:
        intent = intent or classify(user_message)
        session = self.session_store.get(tenant_id=tenant_id, phone=phone)
        status_query = intent.intent in {
            StudentIntent.MY_ENROLLMENTS,
            StudentIntent.PROFILE_LOOKUP,
        } or self.flow._looks_like_enrollment_status_query(user_message)
        if session is None and status_query:
            return AdmissionsAgentResult(
                answer=self.flow.not_registered_status_message(tenant_name=tenant_name),
                tool_output="\n".join(tool_log),
            )

        wants_to_enroll = intent.intent in {
            StudentIntent.ENROLL,
            StudentIntent.AFFIRM,
        } or self.flow._looks_like_enrollment_intent(user_message)

        if session is None and wants_to_enroll:
            session = self.session_store.start(tenant_id=tenant_id, phone=phone)
            tool_log.append("onboarding_session: started")
        elif (
            session is not None
            and not session.active
            and wants_to_enroll
            and resume_onboarding_session(tenant_id=tenant_id, phone=phone)
        ):
            # Picked up where an interrupted enrollment left off, rather than
            # restarting collection from the student's name.
            session = self.session_store.get(tenant_id=tenant_id, phone=phone)
            tool_log.append("onboarding_session: resumed")

        if session is None or not session.active:
            return AdmissionsAgentResult(
                answer=self.flow._t("onboarding_interest", tenant_name=tenant_name),
                tool_output="\n".join(tool_log),
            )

        ob_state = session.to_state()
        classes = await self.crm.list_classes(tenant_id=tenant_id)
        tool_log.append(f"list_classes: {len(classes)} classes")

        if ob_state.awaiting_confirmation:
            ob_state, edited = self.flow.apply_confirmation_edit(
                ob_state,
                user_message,
                classes=classes,
            )
            if edited:
                session = OnboardingSession.from_state(ob_state)
                self.session_store.save(tenant_id=tenant_id, phone=phone, session=session)
                if ob_state.ambiguous_classes:
                    answer = self.flow.disambiguation_prompt(ob_state.ambiguous_classes)
                    return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))
                if not ob_state.awaiting_confirmation:
                    answer = self.flow.prompt_for_step(
                        ob_state.next_step,
                        tenant_name=tenant_name,
                        phone=phone,
                        student_name=ob_state.slots.name,
                        classes=classes if ob_state.next_step == "class" else None,
                        select_rejected=ob_state.invalid_select,
                    )
                    return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))
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

            if self.flow._looks_like_confirm(user_message):
                return await self._commit_onboarding(
                    tenant_id=tenant_id,
                    tenant_name=tenant_name,
                    phone=phone,
                    ob_state=ob_state,
                    classes=classes,
                    tool_log=tool_log,
                )

        if (
            self.flow._looks_like_off_topic_during_onboarding(user_message)
            and not (ob_state.awaiting_confirmation and self.flow._looks_like_reject(user_message))
        ):
            answer = self.flow.prompt_for_step(
                ob_state.next_step,
                tenant_name=tenant_name,
                phone=phone,
                student_name=ob_state.slots.name,
                classes=classes if ob_state.next_step == "class" else None,
                select_rejected=ob_state.invalid_select,
            )
            return AdmissionsAgentResult(answer=answer, tool_output="\n".join(tool_log))

        rejection = self._reject_invalid_slot_value(ob_state, user_message)
        if rejection is not None:
            tool_log.append(f"validation: rejected {ob_state.next_step} — {rejection}")
            prompt = self.flow.prompt_for_step(
                ob_state.next_step,
                tenant_name=tenant_name,
                phone=phone,
                student_name=ob_state.slots.name,
                classes=classes if ob_state.next_step == "class" else None,
                select_rejected=ob_state.invalid_select,
            )
            complaint = t(
                "invalid_registration_value",
                self.flow.language,
                label=_slot_label(ob_state.next_step),
            )
            return AdmissionsAgentResult(
                answer=f"{complaint}\n\n{prompt}",
                tool_output="\n".join(tool_log),
            )

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

        if ob_state.restarted:
            tool_log.append("onboarding_session: restarted")
            return AdmissionsAgentResult(
                answer=self.flow._t("onboarding_restart"),
                tool_output="\n".join(tool_log),
            )

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
            select_rejected=ob_state.invalid_select,
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
        if not self.flow._collection_complete(slots):
            return AdmissionsAgentResult(
                answer=self.flow._t("missing_enrollment_details"),
                tool_output="\n".join(tool_log),
            )

        payload = await self.crm.commit_onboarding(
            tenant_id=tenant_id,
            phone=phone,
            name=slots.name,
            school=slots.school,
            district=slots.district,
            extra_fields=dict(slots.extra),
            class_id=slots.class_id,
            language_pref=self.flow.language,
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

    def _reject_invalid_slot_value(self, ob_state: Any, user_message: str) -> str | None:
        """Reason the message can't be stored in the slot being collected, if any.

        Emoji-only and punctuation-only answers used to be written straight into
        the student record, producing profiles named "💅💅💅" (C1).
        """
        step = ob_state.next_step
        if not step or step == "class" or ob_state.awaiting_confirmation:
            return None
        kind = "name" if step == "name" else _slot_kind(step, self.flow.field_definitions)
        result = validate_registration_value(user_message, field_kind=kind)
        return None if result.ok else result.reason

    async def _class_for_enrollment(
        self, tenant_id: str, class_id: str | None
    ) -> dict[str, Any] | None:
        if not class_id:
            return None
        classes = await self.crm.list_classes(tenant_id=tenant_id)
        return next((c for c in classes if c.get("id") == class_id), None)

    async def _load_field_definitions(self, tenant_id: str, tool_log: list[str]) -> None:
        lister = getattr(self.crm, "list_field_definitions", None)
        if lister is None:
            return
        try:
            rows = await lister(tenant_id=tenant_id)
            self.flow.set_field_definitions(rows)
            tool_log.append(
                f"list_field_definitions: {len(self.flow.field_definitions)} fields"
            )
        except Exception as exc:
            logger.warning("list_field_definitions failed: {}", exc)


def _class_label(class_row: dict[str, Any] | None) -> str:
    row = class_row or {}
    name = row.get("name")
    if name:
        return str(name)
    composed = f"{row.get('grade', '')} {row.get('subject', '')}".strip()
    return composed or "that class"


def _slot_kind(step: str, field_definitions: Any) -> str:
    """Map an onboarding step onto the validation rules for its value."""
    for defn in field_definitions or ():
        if defn.field_key == step:
            return "phone" if defn.field_type in {"phone", "tel"} else "text"
    return "text"


def _slot_label(step: str | None) -> str:
    return (step or "answer").replace("_", " ")


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
