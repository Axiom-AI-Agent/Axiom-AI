# AXIOM AI — Twilio WhatsApp Integration Guide
### For your FastAPI + LangGraph backend, Phase 3 pilot

This is scoped specifically to your architecture: FastAPI as the API gateway/webhook receiver, LangGraph handling routing to your Guardrail/Router → Orchestrator → specialist agents, Supabase for persistence. Twilio's job is narrow and specific: **receive WhatsApp messages and deliver your responses back** — it is not part of your business logic.

---

## 1. Account Setup (15–30 min)

1. Create a Twilio account at twilio.com if you don't have one (free trial credit is enough for a pilot).
2. In the Twilio Console, go to **Messaging → Try it out → Send a WhatsApp message**. This gives you the **WhatsApp Sandbox** — a shared Twilio number you can use immediately without Meta's business verification process.
3. You'll see a **join code** (e.g., "join happy-tiger"). Every participant (your tutor + their students) must send this exact message to the Twilio sandbox number once, from their own WhatsApp, to opt in. This is a real limitation of the sandbox — flag it to your tutor as a one-time step, not a bug.
4. Note down from the console:
   - **Account SID**
   - **Auth Token**
   - **Sandbox WhatsApp number** (format: `whatsapp:+14155238886` typically)

Store these as environment variables — never hardcode them:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## 2. How the Flow Maps to Your Existing Architecture

```
Student sends WhatsApp message
        ↓
Twilio receives it, POSTs to your webhook (FastAPI endpoint)
        ↓
FastAPI parses the incoming request
        ↓
Passed into your existing LangGraph flow
   (Guardrail + Router → Orchestrator fan-out → Agent → Merge)
        ↓
FastAPI sends the response back via Twilio's API
        ↓
Twilio delivers it to the student's WhatsApp
```

**Important:** your LangGraph orchestration logic doesn't change at all. Twilio is purely the transport layer replacing your Demo UI's WebSocket/HTTP connection. Treat this as a new "channel adapter" in front of your existing agent pipeline, not a rebuild.

---

## 3. Install Dependencies

```bash
pip install twilio --break-system-packages
```

Your FastAPI app likely already has `fastapi`, `uvicorn`, and your LangGraph deps installed.

---

## 4. Build the Webhook Endpoint

Twilio needs a **publicly reachable URL** to POST incoming messages to. This is the core integration point.

```python
# app/routers/whatsapp.py

from fastapi import APIRouter, Request, Form
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.responses import Response

router = APIRouter()

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),      # e.g. "whatsapp:+94771234567"
    Body: str = Form(...),      # the message text
    MediaUrl0: str = Form(None),  # present if student sent an image/voice note
    MediaContentType0: str = Form(None),
):
    student_phone = From.replace("whatsapp:", "")

    # Route into your existing LangGraph pipeline
    # This is the same entrypoint your Demo UI already calls
    agent_response = await run_axiom_pipeline(
        tenant_id=get_tenant_for_number(student_phone),  # your multi-tenant lookup
        phone=student_phone,
        message_text=Body,
        media_url=MediaUrl0,
        media_type=MediaContentType0,
    )

    # Respond using TwiML (Twilio's response format)
    twiml = MessagingResponse()
    twiml.message(agent_response.text)

    return Response(content=str(twiml), media_type="application/xml")
```

**Key integration point:** `run_axiom_pipeline(...)` should be the same function/service your Demo UI already calls — this is where you avoid duplicating logic. If your Demo UI currently calls your LangGraph graph directly from a websocket handler, extract that call into a shared function both the Demo UI and this webhook can use.

---

## 5. Critical Constraint: The 3-Second Webhook Window

**This is the single most important technical detail for your use case**, and your own architecture docs already anticipated it (Redis queue for concurrency). Twilio expects a response to its webhook within about **10-15 seconds**, but WhatsApp itself has tighter expectations — if your LangGraph pipeline (LLM calls, RAG retrieval, tool calls) takes longer than a few seconds, the student will see a delayed or failed response.

**Two ways to handle this — pick based on your timeline:**

### Option A (Simpler, fine for pilot scale): Just respond synchronously, but keep it fast
- If your average pipeline response time is under ~5-8 seconds, the synchronous approach above works fine at pilot scale.
- Test this explicitly on Day 1 — measure actual latency from Twilio-received to TwiML-returned.

### Option B (More robust, matches your existing Redis-queue architecture): Async acknowledge + follow-up send
```python
@router.post("/webhook/whatsapp")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    student_phone = From.replace("whatsapp:", "")

    # Immediately acknowledge receipt (empty TwiML = no auto-reply, message queued silently)
    # Queue the actual processing to run async
    await queue_message_for_processing(student_phone, Body)  # e.g. via your Redis queue

    twiml = MessagingResponse()  # empty response, no immediate reply
    return Response(content=str(twiml), media_type="application/xml")

# Separate background worker processes the queue,
# then sends the response proactively using Twilio's REST API (not TwiML reply)
```

For a proactive send (not a webhook reply), use the Twilio client directly:
```python
from twilio.rest import Client

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to_number: str, body: str):
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=f"whatsapp:{to_number}",
        body=body,
    )
```

**Recommendation for your pilot:** start with Option A for speed of implementation today, but keep Option B's pattern in mind — if you already built the Redis queue mentioned in your architecture docs, wiring it in now is a small step and gives you cleaner handling of the confidence-threshold escalation logic you're also building this phase.

---

## 6. Exposing Your Local Backend to Twilio (for testing before deployment)

If you're developing locally before your DigitalOcean droplet is updated, use **ngrok** to tunnel a public URL to your local FastAPI server:

```bash
ngrok http 8000
```

This gives you a temporary public URL like `https://abc123.ngrok-free.app`. Set your Twilio Sandbox webhook to:
```
https://abc123.ngrok-free.app/webhook/whatsapp
```

In Twilio Console: **Messaging → Try it out → WhatsApp Sandbox Settings → "When a message comes in"** field.

**For your actual pilot (not just testing):** point this at your real deployed backend URL (your DigitalOcean droplet, per your README) so it's stable and doesn't depend on your laptop staying online. Set this up as early as possible on Day 1.

---

## 7. Handling Voice Notes (ties into your P0 voice transcription feature)

Twilio delivers voice notes as media attachments, not text. The webhook payload includes `MediaUrl0` and `MediaContentType0` (e.g., `audio/ogg`).

```python
if MediaUrl0 and "audio" in (MediaContentType0 or ""):
    # Download the audio (Twilio requires Basic Auth using your Account SID + Auth Token)
    import requests
    audio_response = requests.get(MediaUrl0, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
    audio_bytes = audio_response.content

    # Transcribe (e.g. via Whisper API), then feed the resulting text
    # into the same pipeline as a normal text message
    transcribed_text = transcribe_audio(audio_bytes)
    Body = transcribed_text  # now flows through the rest of your pipeline unchanged
```

This is exactly the integration point your voice-transcription feature plugs into — Twilio just needs to hand you the raw audio; everything downstream is your existing STT + pipeline work.

---

## 8. Multi-Tenancy: Mapping Phone Numbers to Tutors

Your architecture already isolates by `tenant_id`. For WhatsApp, you need a lookup: **which tutor does this student belong to?**

For a single-tutor pilot, this can be hardcoded/simple:
```python
def get_tenant_for_number(phone: str) -> str:
    # Pilot-scale: single tutor, so this can be a simple constant or a Supabase lookup
    # against a pre-registered student list for this tutor
    return PILOT_TENANT_ID
```

For anything beyond a single pilot tutor, look up the student's registered tutor from Supabase (you likely already have a student→tutor relationship in your schema from the Admissions Agent work).

---

## 9. Testing Checklist Before Going Live with Real Students

- [ ] Send a test text message from your own WhatsApp → confirm it reaches your webhook and a response comes back
- [ ] Time the round-trip latency — is it consistently under ~8 seconds?
- [ ] Test a message that should trigger escalation (e.g., ambiguous/out-of-scope) → confirm it appears on the Staff Dashboard correctly
- [ ] Test resource retrieval (e.g., "send me last week's notes") → confirm Drive/RAG agent responds correctly over WhatsApp formatting (WhatsApp doesn't render markdown the same way your Demo UI might — check formatting)
- [ ] Test a voice note if your transcription feature is ready
- [ ] Confirm your logging/LangFuse tracing captures WhatsApp-originated messages the same way it captures Demo UI messages — this matters for your Phase 3 evidence collection
- [ ] Have your pilot tutor and a few students send the sandbox join code and confirm they're all connected

---

## 10. Known Sandbox Limitations to Flag (be upfront about these, don't get caught off guard)

- **24-hour session window:** WhatsApp Business API (and the Twilio sandbox) restricts free-form messages to within 24 hours of the user's last message. Outside that window, only pre-approved template messages can be sent. For a short pilot with active back-and-forth, this shouldn't bite you — but don't plan on the AI proactively messaging a student who hasn't messaged recently.
- **Join-code friction:** every pilot participant must opt in once. Budget a few minutes of tutor/student onboarding for this on Day 1 — send them the exact join instructions in advance.
- **Shared sandbox number:** you're sharing Twilio's sandbox number with other developers globally (isolated by your own account, but it's not a dedicated production number) — this is expected and fine for a pilot, not something to worry about, just don't market this specific number as a permanent product number.
- **This is explicitly why your MVP doc scoped Twilio over the native Meta API** — faster to stand up, no business verification wait. Migrating to Meta's official WhatsApp Business API is correctly placed in your P1 backlog for after the pilot proves the concept.

---

## Quick Reference: Minimum Working Setup for Today

1. Twilio account + WhatsApp Sandbox activated
2. `/webhook/whatsapp` POST endpoint added to your FastAPI app
3. ngrok tunnel (or deployed URL) set as the sandbox's incoming webhook
4. Your existing LangGraph pipeline called from inside that endpoint
5. TwiML response sent back
6. Tutor + a few students send the join code from their own WhatsApp
7. Send a real test message end-to-end

This should be achievable within a few hours given your pipeline already works — you're wiring a new channel adapter onto an existing, working system, not building new AI logic.
