# AXIOM AI — Telegram Integration: Implementation Plan for Cursor

**Context for the AI assistant:** This is a FastAPI + LangGraph multi-agent backend (AXIOM AI). We are adding Telegram as a new messaging channel, in addition to the existing Demo UI. Multiple tenants (tutors/institutes) each get their own Telegram bot. The existing agent orchestration (Guardrail → Router → Orchestrator → Agents) must NOT be modified — this task is purely a new channel adapter in front of it. Reference the accompanying "AXIOM AI — Telegram Integration Guide" document for full technical rationale; this file is the task breakdown to execute against it.

---

## Pre-requisites (do these manually before starting, not part of the coding task)

- [ ] Create 2 Telegram bots via @BotFather (one per pilot tutor), obtain 2 bot tokens
- [ ] Confirm the existing `run_axiom_pipeline` (or equivalent) function that the Demo UI currently calls — this is the shared entrypoint the Telegram adapter must call. Locate its exact name/location in the codebase before starting Task 1.
- [ ] Confirm existing Supabase schema for `tenant`/`tutor` and `student` tables before starting Task 2.

---

## TASK 1 — Database: Add Telegram Channel Support

**Goal:** Extend the existing schema to support multiple messaging channels per student, and per-tenant bot credentials, without breaking existing tables.

1. Add a `bot_token` and `telegram_bot_username` column to the existing tenant/tutor table (or create a `tenant_config` table if tenant config isn't already centralized — check existing schema first).
2. Create a new `student_channel` table:
   ```sql
   CREATE TABLE student_channel (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       student_id UUID REFERENCES student(id) NOT NULL,
       channel_type TEXT NOT NULL CHECK (channel_type IN ('telegram', 'twilio_whatsapp', 'demo_ui')),
       channel_address TEXT NOT NULL,  -- telegram chat_id, WhatsApp number, etc.
       is_primary BOOLEAN DEFAULT true,
       created_at TIMESTAMPTZ DEFAULT now()
   );
   ```
3. Confirm the existing `student` table has a `student_number` column (phone number) as primary identifier, per SRS. If it doesn't exist yet, add it.
4. Write a migration script consistent with however this project currently manages Supabase migrations (check for an existing `/migrations` folder or Alembic setup before choosing an approach).

**Acceptance criteria:** New tables/columns exist in Supabase; no existing tables/columns are altered or dropped; existing Demo UI functionality is unaffected.

---

## TASK 2 — Config: Per-Tenant Bot Token Storage & Lookup

**Goal:** A function that, given a `tenant_id`, returns the correct Telegram bot token — reading from Supabase, not environment variables (per SRS NFR-17, tenant config must not be hardcoded per deployment).

1. Create `app/services/tenant_config.py` (or place alongside existing tenant/config service if one exists — check first).
2. Implement:
   ```python
   async def get_bot_token_for_tenant(tenant_id: str) -> str:
       # Query the tenant config table/column added in Task 1
       # Raise a clear error if no token is found for this tenant
       ...
   ```
3. Add basic in-memory caching (dict keyed by tenant_id) to avoid hitting Supabase on every incoming message — invalidate/refresh on a reasonable interval (e.g., 5 min) since bot tokens won't change frequently during the pilot.

**Acceptance criteria:** Given a tenant_id, the function reliably returns the correct token; a missing tenant_id fails clearly and loggably, not silently.

---

## TASK 3 — Telegram Client: Send Messages, Fetch Files

**Goal:** A thin, reusable client wrapping Telegram's Bot API — no external SDK needed, plain HTTP via `httpx` (confirm `httpx` is already a project dependency; if not, use whatever async HTTP client is already used elsewhere in the codebase for consistency).

Create `app/services/telegram_client.py`:

```python
import httpx

async def send_telegram_message(tenant_id: str, chat_id: int, text: str) -> None:
    """Send a plain text message to a Telegram chat."""
    ...

async def send_telegram_contact_request(tenant_id: str, chat_id: int, prompt_text: str) -> None:
    """Send a message with a 'Share phone number' button (request_contact keyboard)."""
    ...

async def get_telegram_file_path(tenant_id: str, file_id: str) -> str:
    """Resolve a Telegram file_id to a downloadable file_path via getFile."""
    ...

async def download_telegram_file(tenant_id: str, file_path: str) -> bytes:
    """Download the raw bytes of a Telegram file (image or voice note)."""
    ...
```

Each function must look up the correct bot token via `get_bot_token_for_tenant` from Task 2 before making the API call — never assume a single global token.

**Acceptance criteria:** Each function independently testable/callable; sending a message via any one tenant's bot never touches another tenant's token.

---

## TASK 4 — Webhook Endpoint: Receive & Route Telegram Updates

**Goal:** A FastAPI endpoint that receives Telegram updates, identifies the tenant from the URL path, extracts the message content (text, contact, photo, or voice), and calls the existing agent pipeline.

Create `app/routers/telegram.py`:

```python
from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook/telegram/{tenant_id}")
async def telegram_webhook(tenant_id: str, request: Request):
    update = await request.json()
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")

    # Case 1: contact shared (phone number capture during Admissions)
    if "contact" in message:
        await handle_contact_shared(tenant_id, chat_id, message["contact"])
        return {"ok": True}

    # Case 2: photo (payment slip)
    if "photo" in message:
        await handle_photo_message(tenant_id, chat_id, message["photo"])
        return {"ok": True}

    # Case 3: voice note
    if "voice" in message:
        await handle_voice_message(tenant_id, chat_id, message["voice"])
        return {"ok": True}

    # Case 4: plain text
    if "text" in message:
        await handle_text_message(tenant_id, chat_id, message["text"], message.get("from", {}))
        return {"ok": True}

    return {"ok": True}  # unrecognized update type, acknowledge without action
```

Implement each `handle_*` function in the same file or a `telegram_handlers.py` module:

- `handle_text_message`: look up/resolve student by `chat_id` + `tenant_id` via the `student_channel` table (Task 1), call the existing `run_axiom_pipeline` with the resolved student context and message text, send the response back via `send_telegram_message`.
- `handle_contact_shared`: extract `phone_number` from the contact payload, create/update the student record (`student_number = phone_number`), create a `student_channel` row linking this student to this `chat_id` for `channel_type = 'telegram'`. This is the Admissions phone-capture step — check whether this should call into the existing Admissions Agent flow directly, or be a lightweight pre-step before handing off to it.
- `handle_photo_message`: download the largest photo size via `get_telegram_file_path` + `download_telegram_file`, pass the image bytes into the existing Payment Check Agent flow (locate its current entrypoint from the Demo UI/Twilio path if one exists) exactly as it currently handles payment slip images from other channels.
- `handle_voice_message`: download the voice file, pass to the existing/in-progress voice transcription service (check Task status of the parallel voice-transcription feature being built this same phase — if the transcription function already exists, call it here and feed the resulting text through the same path as `handle_text_message`).

**Acceptance criteria:** A message sent from a real Telegram account to a test bot successfully reaches this endpoint, resolves to the correct tenant, and produces a response sent back to the correct chat_id. Messages to Tutor A's bot never resolve to Tutor B's tenant_id or data.

---

## TASK 5 — Student Resolution Logic

**Goal:** Given a `tenant_id` and a Telegram `chat_id`, determine which student record this message belongs to (or determine that this is a new student who needs Admissions).

Create/extend `app/services/student_resolver.py`:

```python
async def resolve_student(tenant_id: str, channel_type: str, channel_address: str) -> dict | None:
    """
    Look up student_channel joined to student, filtered by tenant_id, channel_type, channel_address.
    Return student record if found, None if this is a new/unregistered contact.
    """
    ...
```

If no student is found, the incoming message should route to the Admissions Agent flow (check how this is currently triggered for new students in the Demo UI/existing pipeline, and replicate that trigger condition here) — and if the very first message isn't a shared contact, prompt for phone number sharing (via `send_telegram_contact_request`) before or as part of that Admissions flow, per the guide's Section 5.

**Acceptance criteria:** A first-time Telegram user is correctly routed into Admissions; a returning user with an existing `student_channel` row is correctly resolved to their existing student record and existing tenant-scoped conversation history/memory.

---

## TASK 6 — Wire Into Existing Pipeline (Critical — Do Not Duplicate Logic)

**Goal:** Confirm and use the exact same pipeline entrypoint the Demo UI (and Twilio integration, if present) already calls — do not write a second, parallel version of the agent orchestration call.

1. Locate the current function/service that the Demo UI calls to process an incoming message (likely something like `run_axiom_pipeline`, `process_message`, or similar — search the codebase for where LangGraph's `.invoke()` or `.ainvoke()` is called for a student message).
2. Confirm its exact signature — parameters, return type — and match `handle_text_message` (Task 4) to call it with the correct arguments: resolved student/tenant context + message text.
3. If this shared function does not yet cleanly support being called from multiple channels (e.g., it's tightly coupled to Demo UI's request/response shape), refactor minimally to accept a channel-agnostic input, but preserve its existing behavior for the Demo UI caller — do not change its output format or business logic.

**Acceptance criteria:** No agent, routing, or RAG logic exists in duplicate between the Demo UI path and the Telegram path. Both channels call the same underlying pipeline function.

---

## TASK 7 — Webhook Registration Script

**Goal:** A small utility script/command to register each tenant's bot webhook with Telegram (this is a one-time setup action per bot, not part of the request-handling code).

Create `scripts/register_telegram_webhook.py`:

```python
import httpx
import asyncio
import sys

async def register_webhook(bot_token: str, tenant_id: str, base_url: str):
    webhook_url = f"{base_url}/webhook/telegram/{tenant_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            params={"url": webhook_url},
        )
        print(resp.json())

if __name__ == "__main__":
    # Usage: python register_telegram_webhook.py <bot_token> <tenant_id> <base_url>
    asyncio.run(register_webhook(sys.argv[1], sys.argv[2], sys.argv[3]))
```

**Acceptance criteria:** Running this script against each pilot bot's token + tenant_id + deployed base URL successfully registers the webhook (verify via `getWebhookInfo` Telegram API call or by sending a test message).

---

## TASK 8 — Logging & Observability Parity

**Goal:** Ensure Telegram-originated conversations are traced the same way Demo UI conversations already are (check existing LangFuse/observability instrumentation).

1. Confirm how the existing pipeline call is currently instrumented for tracing (LangFuse `@observe` decorator or similar, per SRS/README).
2. Ensure that instrumentation captures `channel_type = "telegram"` and `tenant_id` as trace metadata/tags, so Phase 3 evidence collection can filter/report on Telegram-specific usage distinctly if needed.

**Acceptance criteria:** A Telegram-originated conversation appears in the same tracing/observability tool as Demo UI conversations, tagged with channel and tenant.

---

## Suggested Build Order (for a single session with Cursor)

1. Task 1 (DB schema) — foundational, everything else depends on it
2. Task 3 (Telegram client) — self-contained, easy to test in isolation
3. Task 2 (tenant config lookup) — small, needed by Task 3 and 4
4. Task 4 + Task 5 together (webhook + student resolution) — the core integration logic
5. Task 6 (wire into existing pipeline) — do this carefully, this is the "don't break what exists" step
6. Task 7 (webhook registration script) — quick, needed to actually go live
7. Task 8 (logging parity) — do last, lowest risk if skipped under time pressure (but don't skip — it's needed for your Phase 3 evidence)

---

## Explicit Non-Goals for This Task (tell Cursor not to touch these)

- Do NOT modify the LangGraph Guardrail, Router, Orchestrator, or any individual agent's internal logic
- Do NOT modify the Demo UI's existing request/response flow
- Do NOT implement WhatsApp/Twilio in this task — that is a separate, parallel effort
- Do NOT implement Redis/background task queuing for this — Telegram's webhook timeout is lenient enough that synchronous handling is sufficient at pilot scale (see guide, Section 8)
- Do NOT hardcode any bot token, tenant_id, or webhook URL directly in source code — all must come from config/Supabase per Task 2
