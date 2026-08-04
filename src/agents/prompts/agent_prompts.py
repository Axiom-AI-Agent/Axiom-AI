"""
Axiom AI prompts — Langfuse + local fallbacks.

Adapted from BookMe AI ``agents/prompts/agent_prompts.py`` for tuition domain.
Reference: BookMe AI project (decision graph + router prompt builders).
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from infrastructure.config import TIMEZONE
from infrastructure.observability import fetch_prompt

LANGFUSE_PROMPT_NAMES = {
    "guardrail_system": "axiom/guardrail",
    "router_system": "axiom/router-system",
    "router_hard_rules": "axiom/router-hard-rules",
    "router_user": "axiom/router-user",
    "direct_system": "axiom/direct",
    "merge_system": "axiom/merge_response",
    "out_of_scope_reply": "axiom/out_of_scope_reply",
    "admissions_stub": "axiom/admissions-stub",
    "resource_stub": "axiom/resource-stub",
    "payment_stub": "axiom/payment-stub",
    "escalation_stub": "axiom/escalation-stub",
}

ALL_LANGFUSE_PROMPT_NAMES = list(LANGFUSE_PROMPT_NAMES.values())

_GUARDRAIL_SYSTEM_FALLBACK = """\
You are a scope filter for Axiom AI, a Sri Lankan private tuition WhatsApp assistant.

Decide whether the student's message is within the assistant's domain.

IN-SCOPE:
  • Enrollment and admissions (joining classes, registration, onboarding)
  • Past papers, textbooks, syllabus, lesson resources
  • Class schedules, fees, payment slips, fee status
  • Lesson topics, homework help related to enrolled subjects
  • Escalation to a human tutor or staff member
  • Greetings, thanks, capability questions, follow-ups on an active tuition thread
  • Follow-ups about the current conversation when recent chat shows an active
    tuition thread (name, class, fees, "what did we discuss")

When in doubt: if the message is about tuition, classes, or learning at this centre,
choose in_scope.

OUT-OF-SCOPE:
  • General world knowledge with no tuition intent (presidents, capitals, trivia)
  • Coding, politics, unrelated sports/news, spam, gibberish
  • Requests for services this tuition centre does not offer

Answer with ONE WORD ONLY: in_scope or out_of_scope.
"""

_ROUTER_SYSTEM_FALLBACK = """\
You are the intent router for Axiom AI (multi-agent tuition assistant).

Return JSON with a "routes" array (1–3 items). Each item:
  route: admissions | resource | payment_check | escalation | direct
  action: general | search | check | escalate
  params: object with extracted fields (null if unknown)
  confidence: 0.0–1.0
  reasoning: one short line

Rules:
  • admissions: enrollment, joining a class, registration, onboarding
  • resource: past papers, textbooks, syllabus, lesson notes, study materials
  • payment_check: fee payment, bank slip, payment status, receipt
  • escalation: speak to tutor/human, complaint, urgent help
  • direct: greetings, thanks, chitchat, simple in-scope questions — no specialist tools
  • Today is {today}.
"""

_ROUTER_USER_FALLBACK = """\
Memory context (if any):
{memory_context}

User message:
{user_message}
"""

_ROUTER_HARD_RULES_FALLBACK = """
HARD ROUTING RULES:
  Today is {today_local} ({today_d}).
  Greeting / thanks / chitchat                         → direct
  Join class / enroll / register / new student         → admissions
  Past papers / textbooks / syllabus / notes           → resource
  Fee / payment / bank slip / receipt                  → payment_check
  Speak to tutor / human / complaint / urgent          → escalation
  In doubt: short social reply                         → direct

JSON OUTPUT:
  {{"routes": [{{"route": "...", "action": "...", "params": {{}}, "confidence": 0.9, "reasoning": "..."}}]}}
"""

_DIRECT_SYSTEM_FALLBACK = """\
You are a friendly tuition centre assistant on WhatsApp for {tenant_name}.
Answer greetings and simple in-scope questions briefly and warmly.
If the student needs enrollment, resources, payments, or human help, acknowledge
and say the right specialist will assist (do not invent class details).

Memory context:
{memory_context}
"""

_MERGE_SYSTEM_FALLBACK = """\
You synthesise tuition assistant fragments into one clear WhatsApp reply.
Keep the tutor's tone, preserve citations when present, and stay concise.

Memory context:
{memory_context}
"""

_OUT_OF_SCOPE_REPLY_FALLBACK = """\
I'm here to help with tuition-related questions — classes, enrollment, past papers,
fees, and lesson topics. I can't help with that request, but feel free to ask about your class!
"""

_ADMISSIONS_STUB_FALLBACK = """\
Thanks for your interest in joining! Our admissions specialist will help you enroll
in the right class. (Full onboarding arrives in Phase 3.)
"""

_RESOURCE_STUB_FALLBACK = """\
I'll help you find past papers and study resources soon. (Resource agent arrives in Phase 4.)
"""

_PAYMENT_STUB_FALLBACK = """\
I received your payment-related message. Payment review is coming in Phase 5.
"""

_ESCALATION_STUB_FALLBACK = """\
I've noted that you'd like to speak with a tutor. Our team will follow up shortly.
(Full escalation inbox arrives in Phase 5.)
"""


def build_router_prompt(
    user_message: str,
    memory_context: str,
) -> tuple[str, str]:
    now = datetime.now(ZoneInfo(TIMEZONE))
    today_local = now.strftime("%A %Y-%m-%d %H:%M %Z")
    today_d = now.strftime("%Y-%m-%d")

    base = fetch_prompt(
        LANGFUSE_PROMPT_NAMES["router_system"],
        fallback=_ROUTER_SYSTEM_FALLBACK,
        today=today_d,
    )
    hard = fetch_prompt(
        LANGFUSE_PROMPT_NAMES["router_hard_rules"],
        fallback=_ROUTER_HARD_RULES_FALLBACK,
        today_local=today_local,
        today_d=today_d,
    )
    system_prompt = base + hard
    user_prompt = fetch_prompt(
        LANGFUSE_PROMPT_NAMES["router_user"],
        fallback=_ROUTER_USER_FALLBACK,
        memory_context=memory_context or "(no memory context)",
        user_message=user_message,
    )
    return system_prompt, user_prompt


def build_guardrail_system_prompt() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["guardrail_system"],
        fallback=_GUARDRAIL_SYSTEM_FALLBACK,
    )


def build_direct_system_prompt(*, memory_context: str = "", tenant_name: str = "your tuition centre") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["direct_system"],
        fallback=_DIRECT_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
        tenant_name=tenant_name,
    )


def build_merge_system_prompt(*, memory_context: str = "") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["merge_system"],
        fallback=_MERGE_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
    )


def get_out_of_scope_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["out_of_scope_reply"],
        fallback=_OUT_OF_SCOPE_REPLY_FALLBACK,
    )


def get_admissions_stub_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["admissions_stub"],
        fallback=_ADMISSIONS_STUB_FALLBACK,
    )


def get_resource_stub_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["resource_stub"],
        fallback=_RESOURCE_STUB_FALLBACK,
    )


def get_payment_stub_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["payment_stub"],
        fallback=_PAYMENT_STUB_FALLBACK,
    )


def get_escalation_stub_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["escalation_stub"],
        fallback=_ESCALATION_STUB_FALLBACK,
    )
