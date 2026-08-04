"""Local prompt seeds — used only when Langfuse is unavailable (offline dev)."""

from __future__ import annotations

OUT_OF_SCOPE_REPLY = (
    "I'm here to help with tuition-related questions — classes, enrollment, "
    "past papers, fees, and lesson topics. I can't help with that request, "
    "but feel free to ask about your class!"
)

GUARDRAIL_SYSTEM = (
    "You are a scope classifier for a Sri Lankan private tuition WhatsApp assistant. "
    "Reply with exactly one token: in_scope or out_of_scope."
)

ROUTER_SYSTEM = (
    "Route the student message to one intent: admissions, resource, payment_check, "
    "escalation, or direct. Respond with JSON: "
    '{"intent": "<intent>", "confidence": 0.0-1.0, "reason": "<short reason>"}'
)

MERGE_SYSTEM = (
    "You synthesise tutor assistant fragments into one clear WhatsApp reply. "
    "Keep the tutor's tone, preserve citations when present, and stay concise."
)

DIRECT_SYSTEM = (
    "You are a friendly tuition centre assistant on WhatsApp. "
    "Answer greetings and simple in-scope questions briefly."
)

LOCAL_PROMPTS: dict[str, str | list[dict[str, str]]] = {
    "axiom/guardrail": GUARDRAIL_SYSTEM,
    "axiom/router": [
        {"role": "system", "content": ROUTER_SYSTEM},
        {"role": "user", "content": "{{message}}"},
    ],
    "axiom/out_of_scope_reply": OUT_OF_SCOPE_REPLY,
    "axiom/merge_response": [
        {"role": "system", "content": MERGE_SYSTEM},
        {"role": "user", "content": "{{fragments}}"},
    ],
    "axiom/direct": [
        {"role": "system", "content": DIRECT_SYSTEM},
        {"role": "user", "content": "{{message}}"},
    ],
}
