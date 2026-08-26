"""Language detection, mirroring policy, routing, and canned-string eval."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from agents.prompts.agent_prompts import (
    build_direct_system_prompt,
    build_merge_system_prompt,
    get_out_of_scope_reply,
)
from agents.router import heuristic_route
from services.identity.context import IdentityContext
from services.identity.recall_context import format_student_profile
from services.identity.resolver import IdentityResolver
from services.language import (
    detect_script_language,
    language_policy_block,
    normalize_language_pref,
    resolve_reply_language,
    stt_language_hint,
    t,
)


def test_detect_script_sinhala():
    assert detect_script_language("මට පන්තියකට එකතු වෙන්න ඕනේ") == "si"


def test_detect_script_tamil():
    assert detect_script_language("நான் வகுப்பில் சேர விரும்புகிறேன்") == "ta"


def test_detect_script_latin_is_none():
    assert detect_script_language("Sir ada class thiyanawada?") is None
    assert detect_script_language("Sir class notes anuppu") is None
    assert detect_script_language("I want to enroll") is None


def test_resolve_pref_when_latin():
    assert resolve_reply_language(message="ok", language_pref="si") == "si"
    assert resolve_reply_language(message="yes", language_pref="ta") == "ta"


def test_script_overrides_stored_pref():
    assert resolve_reply_language(
        message="நான் notes வேணும்",
        language_pref="si",
    ) == "ta"


def test_normalize_language_pref_aliases():
    assert normalize_language_pref("Sinhala") == "si"
    assert normalize_language_pref("ta-LK") == "ta"
    assert normalize_language_pref("unknown") == "en"
    assert normalize_language_pref(None) == "en"


def test_stt_hint_skips_english():
    assert stt_language_hint("si") == "Sinhala"
    assert stt_language_hint("ta") == "Tamil"
    assert stt_language_hint("en") is None


def test_language_policy_mentions_pref_and_code_switch():
    block = language_policy_block("si")
    assert "Sinhala (si)" in block
    assert "Singlish" in block
    assert "Do not mention this language policy" in block


def test_direct_and_merge_prompts_append_policy():
    direct = build_direct_system_prompt(language_pref="ta")
    merge = build_merge_system_prompt(language_pref="ta")
    assert "LANGUAGE POLICY" in direct
    assert "Tamil (ta)" in direct
    assert "LANGUAGE POLICY" in merge


def test_out_of_scope_localized():
    english = get_out_of_scope_reply()
    sinhala = get_out_of_scope_reply(language="si")
    tamil = get_out_of_scope_reply(language="ta")
    assert "tuition" in english.lower()
    assert sinhala != english
    assert tamil != english
    assert "පන්ති" in sinhala or "ලියාපදිංචි" in sinhala
    assert "வகுப்பு" in tamil or "சேர்க்கை" in tamil


def test_canned_templates_have_en_si_ta():
    assert "voice message" in t("voice_fail", "en").lower()
    assert t("voice_fail", "si") != t("voice_fail", "en")
    assert t("payment_ack", "ta", tenant_name="Demo") != t(
        "payment_ack", "en", tenant_name="Demo"
    )


def test_format_student_profile_includes_language():
    ctx = IdentityContext(
        tenant_id="tenant-demo-physics",
        tenant_slug="demo-physics",
        tenant_name="Demo Physics Academy",
        phone="94771234567",
        session_id="tenant-demo-physics:94771234567",
        student_id="stu-physics-001",
        student_exists=True,
        student_name="Amaya Perera",
        is_enrolled=True,
        enrollment_status="active",
        active_class_names=("A/L Physics 2026",),
        language_pref="si",
    )
    profile = format_student_profile(ctx)
    assert "Sinhala (si)" in profile


def test_identity_resolver_loads_language_pref():
    resolver = IdentityResolver()
    tenant = {
        "id": "tenant-demo-physics",
        "slug": "demo-physics",
        "name": "Demo Physics Academy",
    }
    student = {
        "id": "stu-physics-001",
        "name": "Amaya Perera",
        "language_pref": "ta",
    }
    with (
        patch.object(
            resolver,
            "_lookup_enrollments",
            return_value=[{"class_id": "class-1", "status": "active"}],
        ),
        patch.object(resolver, "_lookup_class_names", return_value={"class-1": "A/L Physics"}),
    ):
        ctx = resolver._build_context(tenant, "94771234567", student)
    assert ctx.language_pref == "ta"


# 5 registers × 4 intents = 20-row routing / detection eval
_EVAL_ROWS = [
    ("en", "enroll", "I want to join A/L Physics", "admissions", None),
    ("en", "notes", "Explain momentum from the uploaded notes", "resource", None),
    ("en", "fees", "I sent my bank slip yesterday", "payment_check", None),
    ("en", "escalate", "Can I speak to the tutor please?", "escalation", None),
    ("si", "enroll", "මට පන්තියකට එකතු වෙන්න ඕනේ", "admissions", "si"),
    ("si", "notes", "මේ පාඩම් notes ටික explain කරන්න", "resource", "si"),
    ("si", "fees", "ගාස්තු ගෙවුවා, slip එක යවනවා", "payment_check", "si"),
    ("si", "escalate", "ගුරුවරයාට කතා කරන්න ඕනේ", "escalation", "si"),
    ("ta", "enroll", "நான் வகுப்பில் சேர விரும்புகிறேன்", "admissions", "ta"),
    ("ta", "notes", "பாடக்குறிப்பு explain பண்ணுங்க", "resource", "ta"),
    ("ta", "fees", "கட்டணம் கட்டிட்டேன், ரசீது அனுப்புறேன்", "payment_check", "ta"),
    ("ta", "escalate", "ஆசிரியரிடம் பேசணும்", "escalation", "ta"),
    ("singlish", "enroll", "class eka join karanna one", "admissions", None),
    ("singlish", "notes", "tute eka ewanna", "resource", None),
    ("singlish", "fees", "fee eka geewuwa slip eka yawanawa", "payment_check", None),
    ("singlish", "escalate", "sir ekata katha karanna one", "escalation", None),
    ("tanglish", "enroll", "class la join panna one", "admissions", None),
    ("tanglish", "notes", "paper eka anuppu", "resource", None),
    ("tanglish", "fees", "fee katti receipt anuppu", "payment_check", None),
    ("tanglish", "escalate", "tutor ekata katha karanna", "escalation", None),
]


@pytest.mark.parametrize(
    ("register", "intent", "message", "expected_route", "expected_script"),
    _EVAL_ROWS,
    ids=[f"{row[0]}-{row[1]}" for row in _EVAL_ROWS],
)
def test_multilingual_intent_eval(
    register: str,
    intent: str,
    message: str,
    expected_route: str,
    expected_script: str | None,
):
    del intent
    assert detect_script_language(message) == expected_script
    assert resolve_reply_language(message=message, language_pref="en") == (
        expected_script or "en"
    )
    decision = heuristic_route(message)
    assert decision is not None, f"heuristic missed: {register} {message}"
    assert decision.primary.route == expected_route
