"""
Axiom AI prompts — Langfuse + local fallbacks.

Structured like BookMe AI ``agents/prompts/agent_prompts.py``:
  • Guardrail — scope filter with tuition-domain examples
  • Router system + hard rules — intent map, param schemas, worked examples
  • Direct / merge — natural WhatsApp tone for specialist synthesis
  • Reply templates — admissions, resources, payments, escalation

Langfuse names use ``axiom/*``. Local fallbacks use Python ``{var}`` syntax.
When seeding ``axiom/router-hard-rules``, JSON examples use ``{{`` in the Python
source so ``.format()`` leaves literal ``{`` for Langfuse Mustache.
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
    "flagged_abusive_reply": "axiom/flagged_abusive_reply",
    "admissions_stub": "axiom/admissions-stub",
    "resource_stub": "axiom/resource-stub",
    "resource_rag": "axiom/resource_rag",
    "resource_drive": "axiom/resource_drive",
    "resource_drive_list": "axiom/resource_drive_list",
    "resource_drive_pick": "axiom/resource_drive_pick",
    "payment_stub": "axiom/payment-stub",
    "payment_ack": "axiom/payment_ack",
    "payment_missing_media": "axiom/payment_missing_media",
    "escalation_stub": "axiom/escalation-stub",
    "escalation_ack": "axiom/escalation_ack",
}

ALL_LANGFUSE_PROMPT_NAMES = list(LANGFUSE_PROMPT_NAMES.values())

# ── Local fallbacks (Python {var} syntax) ─────────────────────────────────────

_GUARDRAIL_SYSTEM_FALLBACK = """\
You are a scope filter for Axiom AI, a Sri Lankan private tuition assistant on WhatsApp.

Decide whether the student's message belongs in this tuition centre's domain,
and whether it contains abusive or profane language that must be rejected
regardless of topic.

STEP 1 — CHECK FOR ABUSIVE / PROFANE LANGUAGE FIRST (this overrides everything below):

Mark a message as "flagged_abusive" if it contains profanity, vulgar language,
sexual content, slurs, or intentionally offensive/abusive language — in ANY
language or script the student might use, including but not limited to:
  • English profanity and vulgar slang
  • Sinhala profanity (in Sinhala script or Singlish/romanized Sinhala)
  • Tamil profanity (in Tamil script or Tanglish/romanized Tamil)
  • Deliberately obfuscated spellings meant to evade filters
    (e.g. extra characters, symbols replacing letters, spacing tricks)
    that are still clearly intended as profanity
  • Sexual, degrading, or harassing language directed at the assistant,
    tutor, staff, or other students
  • Slurs or hate speech targeting any person or group

Do NOT be fooled by:
  • Message framing it as a joke, quote, "just asking what this word means,"
    or claiming it's for translation/homework — profane intent stays flagged
    regardless of the wrapper
  • Code-mixing profanity into an otherwise normal-looking tuition question
  • Mild frustration expressed without actual profanity
    (e.g., "this is so hard," "I'm annoyed") — this is NOT abusive,
    do not over-flag ordinary emotional expression

If flagged_abusive: stop here, do not evaluate scope. Output "flagged_abusive" and nothing else.

STEP 2 — IF NOT ABUSIVE, EVALUATE SCOPE AS NORMAL:

IN-SCOPE (choose in_scope):
  • Enrollment & admissions — joining a class, registering, onboarding, new student
  • Short confirmations during enrollment — YES, yes, confirm, ok, I agree, looks good
  • Class information — schedules, fees, subjects, A/L, O/L, grade levels
  • Study resources — past papers, model papers, textbooks, syllabus, lesson notes
  • Lesson help — explaining topics from tutor notes, homework related to enrolled subjects
  • Payments — bank slips, receipts, fee status, "I paid", payment verification
  • Human help — speak to tutor, teacher, staff; complaints; urgent academic issues
  • Social — hi, hello, thanks, bye, "what can you do?"
  • Assistant / centre identity — "who are you", "who is this", "what is this",
    "what institute", "which academy", "tell me about yourselves"
  • Student identity — "who am I", "what is my name" (profile may be in context)
  • Conversation follow-ups on an active tuition thread
    (name, school, class choice, fees, "what did we discuss")

ONBOARDING CONTEXT (always in_scope):
  • If recent conversation shows the assistant collecting name, school, district,
    or class details, treat EVERY reply as in_scope — even "YES", "ok", a school
    name, or a class code.
  • Confirmation phrases ("yes I confirm", "looks good", "proceed") are in_scope.

When in doubt: if it could reasonably be about this centre, tuition, classes,
learning, or continuing enrollment → in_scope.

Language does not change scope: Sinhala, Tamil, Singlish, Tanglish, and mixed
English messages about tuition are in_scope. Do not mark a message out_of_scope
just because it is not in English.

OUT-OF-SCOPE (choose out_of_scope):
  • General world knowledge with no tuition link (capitals, presidents, trivia)
  • Coding, politics, unrelated sports/news, spam, random gibberish
  • Services this tuition centre does not offer (hotels, travel, medical advice)

Answer with ONE WORD ONLY: flagged_abusive, in_scope, or out_of_scope.
"""

_ROUTER_SYSTEM_FALLBACK = """\
You are the intent router for Axiom AI — a multi-agent tuition assistant on WhatsApp.

Return JSON with a "routes" array (1–3 items). Each item must have:
  route:     admissions | resource | payment_check | escalation | direct
  action:    general | search | check | escalate
  params:    object with extracted fields (use null for unknown — never invent IDs)
  confidence: 0.0–1.0
  reasoning: one short line explaining your choice

Route definitions:
  • admissions    — enrollment, joining a class, registration, onboarding, new student,
                    OR institute info (available classes, fees, centre details, staff/tutor)
  • resource      — tutes, past papers, textbooks, syllabus, PDFs, lesson notes, explain a topic
  • payment_check — fees, bank slip, payment receipt, payment status
  • escalation    — speak to tutor/human, complaint, urgent help needing staff
  • direct        — greetings, thanks, chitchat, "who are you/this", simple in-scope Qs (no tools)

Action hints (downstream agents map these to tools):
  • general  — answer or continue a flow without a search/check tool this turn
  • search   — look up files (Drive) or tutor notes (RAG)
  • check    — verify payment or enrollment status
  • escalate — create a staff escalation ticket

Rules:
  • Do NOT invent student IDs, class IDs, or payment references — use null if missing.
  • Resource + payment in one message → TWO route objects when both intents are clear.
  • Today is {today}.
  • Messages may be English, Sinhala, Tamil, Singlish, or Tanglish. Route by intent,
    not by language. "class eka join karanna", "பாடம் explain பண்ணு", and Sinhala/Tamil
    script questions use the same routes as their English equivalents.
"""

_ROUTER_USER_FALLBACK = """\
Memory context (if any):
{memory_context}

User message:
{user_message}
"""

_ROUTER_HARD_RULES_FALLBACK = """
═════════════════════════════════════════════════════════════════════
HARD ROUTING RULES (non-negotiable — override softer guidance above):
═════════════════════════════════════════════════════════════════════

CONTEXT
  Today is {today_local} (calendar date {today_d}).
  The user is messaging {tenant_name} via WhatsApp.
  Read memory_context before leaving params null — inherit school, class, or
  subject from prior turns when the user says "that one", "same class", etc.

ONBOARDING LOCK (highest priority)
  If memory_context contains "[ONBOARDING IN PROGRESS" or
  "[ONBOARDING AWAITING CONFIRMATION":
    → ALWAYS route to admissions, action general, confidence 1.0
    → Short replies (YES, ok, confirm, a school name, a class name) stay admissions
    → NEVER route onboarding turns to direct or out_of_scope

INTENT MAP (route field)
  Greeting / thanks / chitchat / "what can you do"     → direct
  "Who are you" / "who is this" / "what is this"       → direct (introduce as centre assistant)
  "Who am I" / "what is my name" / "my details"        → direct (profile is in memory_context)
  Join class / enroll / register / new student         → admissions
  What classes / class fees / institute / academy name → admissions (action search — CRM lookup)
  Who is the tutor / staff / contact number            → admissions (action search — CRM lookup)
  Name / school / district / class selection replies   → admissions (if onboarding active)
  YES / confirm / I agree during enrollment review     → admissions
  Tutes / past papers / model papers / textbooks / syllabus / PDFs → resource
  File list or "send me the paper" / download requests → resource
  Numbered follow-up after a file list ("2", "number 3") → resource
  Explain lesson / help me understand / tutor notes    → resource
  Fee / payment / bank slip / receipt / "I paid"       → payment_check
  Speak to tutor / human / complaint / urgent          → escalation
  Class schedule or fee question (enrolled student)    → direct or resource (low confidence ok)
  In doubt: short social reply only                    → direct

OUT OF SCOPE
  Trivia, coding, politics, and unrelated topics are blocked by the guardrail.
  If such a message slipped through, use direct with action general and low confidence.

CONTEXT-FIRST RULE
  Before leaving params null, READ memory_context:
  • Follow-up "same subject" / "that paper" → set params.query or params.subject
  • User picks "the second one" from a class list → set params.class_name or class_id
  • Only omit params when memory_context truly lacks the field.

ACTION MAP (per route)
  admissions:
    general  — onboarding slot collection or enrollment confirmation (default)
    search   — list classes, class fees/details, centre profile, staff/tutor info (CRM)
  resource:
    search   — Drive file lookup OR RAG tutor-note search (set params.query)
    general  — clarify which subject or file type when ambiguous
  payment_check:
    check    — verify fee status when student asks "did you receive my payment?"
    general  — prompt for receipt image when user mentions payment without media
  escalation:
    escalate — create staff ticket (complaint, urgent, speak-to-human)
  direct:
    action MUST be general; params {{}} or simple keys only (no invented IDs)

PARAM SCHEMAS (null if unknown — never guess)
  admissions params:  student_name, school, district, class_name, class_id, grade (A/L|O/L)
  resource params:    query, subject, grade, folder (papers|textbooks|syllabus)
  payment_check params: amount, reference, month
  escalation params:  reason, urgency
  direct params:      {{}} (usually empty)

RESOURCE SUB-ROUTING HINT
  • File/download requests (tutes, papers, PDFs, textbooks, syllabus) → resource/search
  • Explanation requests ("explain photosynthesis", "what did sir teach") → resource/search, query = user message
  • Classify by intent, not a fixed phrase. Any request to get or list class files is resource.

ROUTING EXAMPLES:

  "hi" / "hello" / "thanks"
    → direct {{action: "general", params: {{}}}}

  "who are you?" / "who is this?" / "what is this?"
    → direct {{action: "general", params: {{}}}}

  "I want to join A/L Physics"
    → admissions {{action: "general", params: {{class_name: "A/L Physics", grade: "A/L"}}}}

  "My name is Amaya Perera" (memory shows ONBOARDING collecting name)
    → admissions {{action: "general", params: {{student_name: "Amaya Perera"}}}}

  "YES" / "yes I confirm" (memory shows ONBOARDING AWAITING CONFIRMATION)
    → admissions {{action: "general", params: {{}}}}

  "What classes do you offer?"
    → admissions {{action: "search", params: {{}}}}

  "What are the classes that are available currently?"
    → admissions {{action: "search", params: {{}}}}

  "How much is A/L Physics?"
    → admissions {{action: "search", params: {{grade: "A/L", subject: "Physics"}}}}

  "Who is the tutor?"
    → admissions {{action: "search", params: {{}}}}

  "Tell me about Demo Physics Academy"
    → admissions {{action: "search", params: {{}}}}

  "Do you have 2023 Physics past papers?"
    → resource {{action: "search", params: {{query: "2023 Physics past papers", subject: "Physics", folder: "papers"}}}}

  "any tutes?" / "send me the papers"
    → resource {{action: "search", params: {{folder: "papers"}}}}

  "what textbooks do you have" / "send me the text books"
    → resource {{action: "search", params: {{folder: "textbooks"}}}}

  "I need the syllabus PDF"
    → resource {{action: "search", params: {{folder: "syllabus"}}}}

  "2" (memory shows the assistant listed numbered Drive files)
    → resource {{action: "search", params: {{}}}}

  "Can you explain the mole concept from last week's notes?"
    → resource {{action: "search", params: {{query: "mole concept", folder: "notes"}}}}

  "I sent my bank slip for January fees"
    → payment_check {{action: "general", params: {{month: "January"}}}}

  "Did you receive my payment?"
    → payment_check {{action: "check", params: {{}}}}

  "I need to speak to the tutor urgently"
    → escalation {{action: "escalate", params: {{reason: "speak to tutor", urgency: "high"}}}}

  "What's the capital of France?"
    → direct {{action: "general", params: {{}}}}, confidence 0.3
    (guardrail should catch this; low confidence if it slipped through)

FOLLOW-UP EXAMPLES (use memory_context):

  Previous turn: assistant listed A/L classes.
  User: "I'll take Physics"
    → admissions {{action: "general", params: {{class_name: "A/L Physics"}}}}

  Previous turn: assistant shared Physics past paper links.
  User: "any for 2022 as well?"
    → resource {{action: "search", params: {{query: "2022 Physics past papers", subject: "Physics"}}}}

  Previous turn: enrollment complete, payment requested.
  User: [image attached — no text]
    → payment_check {{action: "general", params: {{}}}}

JSON OUTPUT REMINDER
  Return ONLY valid JSON:
  {{"routes": [{{"route": "...", "action": "...", "params": {{...}}, "confidence": 0.9, "reasoning": "..."}}]}}
"""

_DIRECT_SYSTEM_FALLBACK = """\
You are the friendly WhatsApp assistant for {tenant_name}.

Your role:
  • Greet students and answer simple in-scope questions about the centre.
  • Handle general chat when admissions, resources, or payments are not needed.
  • For live class lists, fees, centre details, tutors, or staff — say you can look that up
    (admissions handles CRM); do NOT invent those facts.
  • For enrollment, past papers, payment help, or a human tutor — acknowledge clearly.
    Do NOT invent class names, fees, schedules, or enrollment status.

When asked "who are you", "who is this", or "what is this":
  • Introduce yourself as the AI assistant for {tenant_name}.
  • Briefly say you help with joining classes, past papers, lesson topics, fees,
    and speaking to a tutor.
  • Invite them to ask about enrollment or their class. Keep it to 2–3 short sentences.

When asked "who am I", "what is my name", or similar:
  • If the profile below has a name/class, answer with those facts warmly.
  • If they are an unknown visitor, say you do not have their details yet and offer enrollment.
  • Do NOT claim you lack personal information when profile data is present below.

Known student profile (from CRM):
{student_profile_context}

Tone & format:
  • Warm, clear, concise — like a helpful tuition centre admin.
  • WhatsApp-friendly: short paragraphs; bullets when listing options.
  • Plain text only — never use markdown markers such as **bold**.
  • Use the student's name from the profile or memory_context when known.
  • Sri Lankan context is fine (A/L, O/L, rupees, local school names).

Do NOT:
  • Make up prices, class times, or availability.
  • Promise instant enrollment or payment approval.
  • Answer out-of-scope trivia (politics, coding, general knowledge).
  • Repeat, translate, or use abusive or profane language. Never echo swear words.

Memory context:
{memory_context}
"""

_MERGE_SYSTEM_FALLBACK = """\
You merge outputs from multiple Axiom AI specialist agents into one coherent WhatsApp reply.

Inputs you receive:
  • FRAGMENTS — labelled blocks from admissions, resource, payment_check, escalation agents
  • The student's original message

Your task:
  1. Read all fragments and the user message.
  2. Combine them into a single, natural reply — no duplicate greetings or sign-offs.
  3. Preserve factual details exactly: class names, file links, citations, payment instructions.
  4. Keep the warm tuition-centre tone. Short paragraphs; bullets when listing items.
  5. Plain text only — never use markdown markers such as **bold**.
  6. If one fragment failed or is empty, rely on the others — do not mention internal errors.
  7. Do NOT add facts, links, or promises not present in the fragments.
  8. Never repeat, translate, or include abusive or profane language from the student or fragments.

Memory context (for tone and follow-up continuity):
{memory_context}
"""

_OUT_OF_SCOPE_REPLY_FALLBACK = """\
I'm here to help with tuition-related things — joining classes, past papers, lesson topics, fees, and speaking to your tutor.

That question is a bit outside what I can help with here. Feel free to ask me about your class or enrollment!
"""

_FLAGGED_ABUSIVE_REPLY_FALLBACK = """\
I can't help with messages that use abusive or offensive language.

Please rephrase your question about classes, enrollment, or your studies — I'm happy to help with that.
"""

_ADMISSIONS_STUB_FALLBACK = """\
Hi! Welcome to {tenant_name}. I'm the AI assistant here — I can help with classes, past papers, fees, and speaking to a tutor.

If you'd like to register or enroll, just say so and I'll get you started.
"""

_RESOURCE_NOT_ENROLLED_FALLBACK = """\
Past papers and tutor notes are available to enrolled students only.

Reply "join class" or complete your enrollment at {tenant_name} to get access!
"""

_RESOURCE_STUB_FALLBACK = """\
I'll look that up for you — searching our past papers and tutor notes now.
"""

_RESOURCE_RAG_FALLBACK = """\
Based on your tutor's notes:

{answer}

Sources: {citations}
"""

_RESOURCE_DRIVE_FALLBACK = """\
Here are the files I found for "{query}":

{file_list}
"""

_RESOURCE_DRIVE_LIST_FALLBACK = """\
Here are the available {folder_label}:

{file_list}

Reply with the number of the file you want.
"""

_RESOURCE_DRIVE_LIST_RANGE_FALLBACK = """\
That number is not on the list. Reply with a number from 1 to {count}:

{file_list}
"""

_RESOURCE_DRIVE_PICK_FALLBACK = """\
Here's the file you picked:

{filename}
{link}
"""

_RESOURCE_DRIVE_EMPTY_FALLBACK = (
    "I couldn't find any {folder_label} in Drive right now. "
    "Please check with {tenant_name}."
)

_RESOURCE_RAG_ERROR_FALLBACK = (
    "Sorry — I couldn't search the tutor notes right now. "
    "Please try again in a moment or ask your tutor directly."
)

_RESOURCE_DRIVE_ERROR_FALLBACK = (
    "Sorry — I couldn't search for files right now. "
    "Please try again in a moment or contact your tuition centre."
)

_PAYMENT_STUB_FALLBACK = """\
Got your payment message — I'll help get that verified with the team at {tenant_name}.
"""

_PAYMENT_ACK_FALLBACK = """\
Thanks! We received your payment receipt for {tenant_name}.

Our team will verify it shortly and confirm your enrollment. You'll hear back here on WhatsApp once it's approved.
"""

_PAYMENT_MISSING_MEDIA_FALLBACK = """\
To verify your payment at {tenant_name}, please send a clear photo of your bank slip or payment receipt.

Once we have the image, our team can review and confirm your enrollment.
"""

_ESCALATION_STUB_FALLBACK = """\
I've noted that you'd like to speak with someone from the team. A tutor or staff member will follow up with you shortly.
"""

_ESCALATION_ACK_FALLBACK = """\
We've notified your tutor at {tenant_name}. They'll get back to you soon.

You can keep chatting here in the meantime — I'm still happy to help with class questions or resources.
"""


# ── Builders (always go through fetch_prompt) ─────────────────────────────────

def build_router_prompt(
    user_message: str,
    memory_context: str,
    *,
    tenant_name: str = "your tuition centre",
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
        tenant_name=tenant_name,
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


def build_direct_system_prompt(
    *,
    memory_context: str = "",
    tenant_name: str = "your tuition centre",
    student_profile_context: str = "",
    language_pref: str = "en",
) -> str:
    from services.language import with_language_policy

    prompt = fetch_prompt(
        LANGFUSE_PROMPT_NAMES["direct_system"],
        fallback=_DIRECT_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
        tenant_name=tenant_name,
        student_profile_context=student_profile_context or "(no student profile on file)",
    )
    return with_language_policy(prompt, language_pref)


def build_merge_system_prompt(
    *,
    memory_context: str = "",
    language_pref: str = "en",
) -> str:
    from services.language import with_language_policy

    prompt = fetch_prompt(
        LANGFUSE_PROMPT_NAMES["merge_system"],
        fallback=_MERGE_SYSTEM_FALLBACK,
        memory_context=memory_context or "(none)",
    )
    return with_language_policy(prompt, language_pref)


def get_out_of_scope_reply(*, language: str = "en") -> str:
    from services.language import normalize_language_pref, t

    lang = normalize_language_pref(language)
    if lang != "en":
        return t("out_of_scope", lang)
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["out_of_scope_reply"],
        fallback=_OUT_OF_SCOPE_REPLY_FALLBACK,
    )


def get_flagged_abusive_reply(*, language: str = "en") -> str:
    from services.language import normalize_language_pref, t

    lang = normalize_language_pref(language)
    if lang != "en":
        return t("flagged_abusive", lang)
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["flagged_abusive_reply"],
        fallback=_FLAGGED_ABUSIVE_REPLY_FALLBACK,
    )


def get_admissions_stub_reply(*, tenant_name: str = "our tuition centre") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["admissions_stub"],
        fallback=_ADMISSIONS_STUB_FALLBACK,
        tenant_name=tenant_name,
    )


def get_resource_not_enrolled_reply(
    *,
    tenant_name: str = "our tuition centre",
    language: str = "en",
) -> str:
    from services.language.detect import normalize_canned_language
    from services.language import t

    lang = normalize_canned_language(language)
    if lang != "en":
        return t("resource_not_enrolled", lang, tenant_name=tenant_name)
    return fetch_prompt(
        "axiom/resource-not-enrolled",
        fallback=_RESOURCE_NOT_ENROLLED_FALLBACK,
        tenant_name=tenant_name,
    )


def get_resource_stub_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["resource_stub"],
        fallback=_RESOURCE_STUB_FALLBACK,
    )


def build_resource_rag_reply(
    *,
    answer: str,
    citations: list[dict] | None = None,
    error: str | None = None,
    language: str = "en",
) -> str:
    from services.language.detect import normalize_canned_language
    from services.language import t

    lang = normalize_canned_language(language)
    if error:
        if lang != "en":
            return t("rag_search_error", lang)
        return _RESOURCE_RAG_ERROR_FALLBACK
    if not answer:
        return t("rag_empty", lang)
    cite_parts = []
    for c in citations or []:
        lesson = c.get("lesson")
        title = c.get("title") or "notes"
        if lesson:
            cite_parts.append(f"[lesson: {lesson}] {title}")
        elif title:
            cite_parts.append(title)
    citations_str = ", ".join(cite_parts) if cite_parts else "tutor notes"
    if lang != "en":
        return t("resource_rag_header", lang, answer=answer, citations=citations_str)
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["resource_rag"],
        fallback=_RESOURCE_RAG_FALLBACK,
        answer=answer,
        citations=citations_str,
    )


def _drive_folder_label(folder: str | None, *, language: str = "en") -> str:
    from services.language.detect import normalize_canned_language
    from services.language import t

    key = (folder or "papers").strip().lower()
    lang = normalize_canned_language(language)
    folder_keys = {
        "papers": "drive_folder_papers",
        "textbooks": "drive_folder_textbooks",
        "syllabus": "drive_folder_syllabus",
    }
    return t(folder_keys.get(key, "drive_folder_files"), lang)


def _numbered_drive_names(files: list[dict]) -> str:
    class_names = {str(item.get("class_name") or "").strip() for item in files}
    class_names.discard("")
    show_class = len(class_names) > 1
    lines = []
    for index, item in enumerate(files, start=1):
        name = str(item.get("name") or "file").strip() or "file"
        class_name = str(item.get("class_name") or "").strip()
        if show_class and class_name:
            lines.append(f"{index}. {name} ({class_name})")
        else:
            lines.append(f"{index}. {name}")
    return "\n".join(lines)


def build_resource_drive_list_reply(
    *,
    files: list[dict],
    folder: str = "papers",
    tenant_name: str = "your tuition centre",
    error: str | None = None,
    empty_message: str | None = None,
    out_of_range: bool = False,
    language: str = "en",
) -> str:
    from services.language.detect import normalize_canned_language
    from services.language import t

    lang = normalize_canned_language(language)
    label = _drive_folder_label(folder, language=lang)
    if error:
        if lang != "en":
            return t("drive_error", lang)
        return _RESOURCE_DRIVE_ERROR_FALLBACK
    if not files:
        if empty_message:
            return empty_message
        if lang != "en":
            return t("drive_empty", lang, folder_label=label, tenant_name=tenant_name)
        return _RESOURCE_DRIVE_EMPTY_FALLBACK.format(
            folder_label=label,
            tenant_name=tenant_name,
        )
    file_list = _numbered_drive_names(files)
    if out_of_range:
        if lang != "en":
            return t("drive_list_range", lang, count=len(files), file_list=file_list)
        return _RESOURCE_DRIVE_LIST_RANGE_FALLBACK.format(count=len(files), file_list=file_list)
    if lang != "en":
        return t(
            "drive_list",
            lang,
            folder_label=label,
            file_list=file_list,
            tenant_name=tenant_name,
        )
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["resource_drive_list"],
        fallback=_RESOURCE_DRIVE_LIST_FALLBACK,
        folder_label=label,
        file_list=file_list,
        tenant_name=tenant_name,
    )


def build_resource_drive_pick_reply(
    *,
    name: str,
    link: str,
    tenant_name: str = "your tuition centre",
    language: str = "en",
) -> str:
    from services.language.detect import normalize_canned_language
    from services.language import t

    lang = normalize_canned_language(language)
    if lang != "en":
        return t(
            "drive_pick",
            lang,
            filename=name,
            link=link.strip() or "(link unavailable)",
            tenant_name=tenant_name,
        )
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["resource_drive_pick"],
        fallback=_RESOURCE_DRIVE_PICK_FALLBACK,
        filename=name,
        link=link.strip() or "(link unavailable)",
        tenant_name=tenant_name,
    )


def build_resource_drive_reply(
    *,
    files: list[dict],
    query: str,
    tenant_name: str = "your tuition centre",
    error: str | None = None,
    empty_message: str | None = None,
    language: str = "en",
) -> str:
    del query
    return build_resource_drive_list_reply(
        files=files,
        tenant_name=tenant_name,
        error=error,
        empty_message=empty_message,
        language=language,
    )


def get_payment_stub_reply(*, tenant_name: str = "our tuition centre") -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["payment_stub"],
        fallback=_PAYMENT_STUB_FALLBACK,
        tenant_name=tenant_name,
    )


def build_payment_ack_reply(
    *,
    tenant_name: str = "our tuition centre",
    language: str = "en",
) -> str:
    from services.language import normalize_language_pref, t

    lang = normalize_language_pref(language)
    if lang != "en":
        return t("payment_ack", lang, tenant_name=tenant_name)
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["payment_ack"],
        fallback=_PAYMENT_ACK_FALLBACK,
        tenant_name=tenant_name,
    )


def build_payment_missing_media_reply(
    *,
    tenant_name: str = "our tuition centre",
    language: str = "en",
) -> str:
    from services.language import normalize_language_pref, t

    lang = normalize_language_pref(language)
    if lang != "en":
        return t("payment_missing_media", lang, tenant_name=tenant_name)
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["payment_missing_media"],
        fallback=_PAYMENT_MISSING_MEDIA_FALLBACK,
        tenant_name=tenant_name,
    )


def get_escalation_stub_reply() -> str:
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["escalation_stub"],
        fallback=_ESCALATION_STUB_FALLBACK,
    )


def build_escalation_ack_reply(
    *,
    tenant_name: str = "our tuition centre",
    language: str = "en",
) -> str:
    from services.language import normalize_language_pref, t

    lang = normalize_language_pref(language)
    if lang != "en":
        return t("escalation_ack", lang, tenant_name=tenant_name)
    return fetch_prompt(
        LANGFUSE_PROMPT_NAMES["escalation_ack"],
        fallback=_ESCALATION_ACK_FALLBACK,
        tenant_name=tenant_name,
    )
