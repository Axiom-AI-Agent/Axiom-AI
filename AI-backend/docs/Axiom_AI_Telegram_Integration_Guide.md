# AXIOM AI — Telegram Integration Guide
### Multi-Bot, Multi-Tenant Architecture — Mapped to SRS Section 7 (System Architecture) & 7.5 (Multi-Tenancy Model)

This guide is written specifically against what's already in your SRS: `tenant_id`-scoped isolation, `student_number` as the primary student identifier, PDPA consent capture at Admissions, and the LangGraph orchestrator (Guardrail → Router → Orchestrator fan-out → Agents). Telegram becomes a new channel adapter in front of that same pipeline — same pattern as the Twilio integration, no change to your agent logic.

---

## 1. Why "One Bot Per Tutor/Institute" Is the Right Call

You asked for separate bots per organization rather than one shared bot — this is actually a **better fit for your SRS** than a shared-number model would be, for a specific reason:

Your SRS (7.5) states tenant isolation is enforced *at the data layer* via `tenant_id`, and that "Google Drive/MCP access is scoped per-tutor from the ground up." With Telegram, you have a choice most teams don't get with WhatsApp: **you can make tenant isolation visible at the channel level too**, not just the database level. Each tutor/institute gets their own bot with their own name and identity (e.g., `@MrPereraTutorBot`, `@BrightAcademyBot`) — this reads as more professional and trustworthy to real tutors evaluating whether to adopt you, since their students are messaging *their* branded assistant, not a shared generic one.

**Technically, this means:** each bot has its own Telegram Bot API token, and each token maps to exactly one `tenant_id` in your system. The webhook URL itself can encode which tenant a given bot belongs to, so incoming messages self-identify their tenant before they even hit your routing logic.

---

## 2. Creating a Bot (per tutor/institute) — 2 Minutes Each

1. Open Telegram, search for **@BotFather** (Telegram's official bot for creating bots).
2. Send `/newbot`.
3. Give it a display name (e.g., "Mr. Perera's Tutor Assistant") and a unique username ending in `bot` (e.g., `MrPereraTutorBot`).
4. BotFather returns an **API token** — this is the credential for this specific tutor's bot. Treat it like a password.

Repeat this once per pilot tutor/institute — for your two-tutor validation, do this twice, giving you two tokens.

Store them scoped to tenant, not as generic env vars:
```
# Example structure — store in Supabase (tenant config table) or a secrets manager,
# not hardcoded, since you'll add more tutors over time
TELEGRAM_BOT_TOKEN_TENANT_A=123456:ABC-DEF...
TELEGRAM_BOT_TOKEN_TENANT_B=789012:GHI-JKL...
```

Per your SRS NFR-17 ("Tutor-specific configuration shall be managed as tenant-level data, not hardcoded per deployment"), the correct place for this is a **tenant configuration table in Supabase** — e.g., a `bot_token` and `telegram_bot_username` column on your existing tenant/tutor record — not environment variables per tutor, which wouldn't scale past your pilot and would violate the pattern you already committed to.

---

## 3. Webhook Architecture — One Endpoint, Tenant Identified by URL Path

Telegram bots receive updates via webhook, similar to Twilio. The clean way to handle multiple bots in one FastAPI service is to **encode the tenant in the webhook path itself**, so Telegram tells you which bot (and therefore which tenant) a message belongs to before you even parse the payload.

```python
# app/routers/telegram.py

from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook/telegram/{tenant_id}")
async def telegram_webhook(tenant_id: str, request: Request):
    update = await request.json()

    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")
    telegram_user = message.get("from", {})

    # tenant_id comes directly from the URL — no ambiguity, no lookup needed
    response_text = await run_axiom_pipeline(
        tenant_id=tenant_id,
        channel="telegram",
        channel_user_id=str(chat_id),
        message_text=text,
        telegram_meta=telegram_user,
    )

    await send_telegram_message(tenant_id, chat_id, response_text)
    return {"ok": True}
```

When registering each bot's webhook with Telegram, set the URL to include that tutor's tenant ID:
```
https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://yourdomain.com/webhook/telegram/<tenant_id>
```

This is a clean architectural fit with your existing multi-tenant model — `run_axiom_pipeline` is the exact same function your Demo UI and (if you proceed with it later) Twilio integration call. Only the channel adapter differs.

---

## 4. Sending Responses Back

```python
import httpx

async def send_telegram_message(tenant_id: str, chat_id: int, text: str):
    bot_token = get_bot_token_for_tenant(tenant_id)  # lookup from Supabase tenant config
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})
```

No SDK strictly required — Telegram's Bot API is plain REST/JSON, which is arguably simpler to integrate than Twilio's TwiML response format.

---

## 5. Solving Your Core Requirement: Identifying the Student by Phone Number

This is the part worth being precise about, since it doesn't work quite the same as WhatsApp/Twilio.

**The problem:** Telegram's `chat_id` is a Telegram-internal identifier — it is *not* a phone number, and Telegram does not expose a user's phone number by default for privacy reasons. Your SRS (Section 8) states `student_number` is your primary student identifier. So you need an explicit step to capture it.

**The solution: Telegram's native "Share Contact" button, requested during Admissions.**

This actually fits your existing Admissions Agent flow perfectly — your SRS already describes the Admissions Agent asking for Name, School, Grade/Subject, *and* PDPA consent before creating a student record. Add phone number capture as one more field in that same flow, using Telegram's built-in contact-sharing UI (so the student taps a button rather than typing their number, which is faster and less error-prone):

```python
async def request_phone_number(tenant_id: str, chat_id: int):
    bot_token = get_bot_token_for_tenant(tenant_id)
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    keyboard = {
        "keyboard": [[{"text": "Share my phone number", "request_contact": True}]],
        "one_time_keyboard": True,
        "resize_keyboard": True,
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json={
            "chat_id": chat_id,
            "text": "To complete your registration, please share your phone number.",
            "reply_markup": keyboard,
        })
```

When the student taps the button, Telegram sends a `contact` object in the next webhook update instead of a plain `text` message:
```python
contact = message.get("contact")
if contact:
    phone_number = contact.get("phone_number")  # this becomes your student_number
    telegram_chat_id = message.get("chat", {}).get("id")
    # Create/update the student record: student_number = phone_number,
    # with telegram_chat_id stored alongside it as the delivery address for this channel
```

**Important architectural point, matching your SRS Section 8 note:** *"student_number is used as the primary identifier rather than contact ID alone, since a student's phone number/contact detail may change over time."* This means your student record should store **both** fields:
- `student_number` (phone number) — the durable, primary identity, consistent with your data model and with WhatsApp/Twilio if you add it later
- `telegram_chat_id` — the channel-specific delivery address, used only to know *where* to send Telegram messages for this student right now

If a student's Telegram chat_id ever needs to change (new device, re-added bot, etc.), you update the channel address without touching their core identity — directly consistent with NFR-24 ("support updating a student's contact number/details without loss of history").

---

## 6. Data Model Addition (small, additive change to your existing schema)

Per SRS Section 8, extend your student/conversation model with channel awareness rather than assuming WhatsApp/Twilio as the only channel:

```
student
  - student_id (PK)
  - student_number       -- primary identifier (phone number)
  - name, school, grade/subject
  - tenant_id (FK)
  - pdpa_consent (bool, timestamp)

student_channel
  - student_id (FK)
  - channel_type          -- "telegram" | "twilio_whatsapp" | "demo_ui"
  - channel_address        -- telegram chat_id, or WhatsApp number, etc.
  - is_primary
```

This small `student_channel` table means a student could, in principle, be reachable across multiple channels later (matches your NFR-16 extensibility requirement: new channels shouldn't require changes to existing agent logic) — but for your pilot, you'll just have one row per student with `channel_type = "telegram"`.

---

## 7. Handling Images (Payment Slips) and Voice Notes — Both Native to Telegram

Telegram handles both natively and arguably more simply than Twilio:

```python
photo = message.get("photo")       # list of image sizes, largest last
voice = message.get("voice")       # voice note object, has file_id

if photo:
    file_id = photo[-1]["file_id"]  # highest resolution
    file_path = await get_telegram_file_path(tenant_id, file_id)
    image_bytes = await download_telegram_file(tenant_id, file_path)
    # → feeds into your Payment Check Agent exactly as a WhatsApp image would

if voice:
    file_id = voice["file_id"]
    file_path = await get_telegram_file_path(tenant_id, file_id)
    audio_bytes = await download_telegram_file(tenant_id, file_path)
    # → feeds into your voice transcription pipeline, same as planned for WhatsApp
```

```python
async def get_telegram_file_path(tenant_id: str, file_id: str) -> str:
    bot_token = get_bot_token_for_tenant(tenant_id)
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.telegram.org/bot{bot_token}/getFile", params={"file_id": file_id})
        return r.json()["result"]["file_path"]

async def download_telegram_file(tenant_id: str, file_path: str) -> bytes:
    bot_token = get_bot_token_for_tenant(tenant_id)
    async with httpx.AsyncClient() as client:
        r = await client.get(f"https://api.telegram.org/file/bot{bot_token}/{file_path}")
        return r.content
```

This directly feeds your Payment Check Agent (SRS Section 2, Payment escalation flow) and your P0 voice transcription feature with no additional adapter logic needed beyond this.

---

## 8. No Webhook Timeout Pressure (unlike Meta's WhatsApp 3-second rule)

Your SRS explicitly notes Twilio was chosen partly *because* Meta's native API imposes a strict 3-second webhook response window. **Telegram does not impose this same aggressive constraint** — Telegram's webhook timeout is considerably more forgiving (documented around 60 seconds acceptable response time before Telegram considers retrying). This means:

- You likely do **not** need a Redis queue or background task pattern for Telegram specifically, even more so than the earlier Twilio discussion concluded
- A straightforward synchronous call to your LangGraph pipeline inside the webhook handler is safe for pilot scale
- This removes one more piece of infrastructure complexity from your already-tight timeline

---

## 9. Compliance With Your Existing NFRs — Quick Checklist

| SRS Requirement | How Telegram Integration Satisfies It |
|---|---|
| NFR-06 (encryption in transit/at rest) | Telegram's Bot API is HTTPS-only by default; your Supabase storage already handles at-rest encryption |
| NFR-07 (strict tenant isolation) | Enforced structurally — each bot token + webhook path is tied to exactly one `tenant_id`, isolation happens before the message even reaches your router |
| NFR-08 (PDPA consent at registration) | Consent capture step in Admissions Agent is unchanged; phone number capture is simply added as one more field in that same flow |
| NFR-12 (graceful degradation, no silent drops) | Wrap `send_telegram_message` calls in retry logic; Telegram's API returns clear error codes (e.g., bot blocked by user) you can log and escalate on |
| NFR-14 (no separate app/account required) | Fully satisfied — Telegram is a messaging app students already have or can install in seconds, same principle as WhatsApp |
| NFR-16 (new agents addable without changing existing logic) | Fully satisfied — Telegram is purely a new channel adapter; zero changes to Guardrail/Router/Orchestrator/Agents |

---

## 10. Setup Checklist for Your Two-Tutor Pilot

- [ ] Create Bot 1 via BotFather for Tutor A, note token
- [ ] Create Bot 2 via BotFather for Tutor B, note token
- [ ] Store both tokens in Supabase tenant config table, not hardcoded
- [ ] Deploy `/webhook/telegram/{tenant_id}` endpoint
- [ ] Register each bot's webhook URL with its respective tenant_id path
- [ ] Extend Admissions Agent flow to request phone number via Telegram's contact-share button, store as `student_number`
- [ ] Add `student_channel` table (or equivalent) to track `telegram_chat_id` per student
- [ ] Test end-to-end with your own Telegram account against each bot separately — confirm tenant isolation (Tutor A's bot never returns Tutor B's data)
- [ ] Send both tutors their bot's username/link — this is all onboarding requires, no join code, no verification wait
- [ ] Test image (payment slip) and voice note handling if those features are ready

---

## Why This Is a Stronger Phase 3 Story Than the WhatsApp Route Right Now

- **Zero external approval dependency** — nothing here is blocked by Meta or Twilio review timelines
- **Two distinct, branded bots for two real tutors** — arguably a *more* convincing multi-tenant demonstration for judges than one shared WhatsApp sandbox number, since it visibly proves tenant isolation rather than just asserting it
- **Directly extends, not replaces, your architecture** — every SRS requirement above still holds; you're adding a channel adapter, not changing your system design
- **Matches your own roadmap** — Telegram Bot API integration is already documented as a planned direction in your README and backlog, so this isn't an improvised detour, it's you executing a decision you'd already scoped, just moved earlier because it fits your real constraint this week
