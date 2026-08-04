# Dev Chat — WhatsApp Simulator (No Twilio Required)

Use the HTTP chat API during local development instead of configuring the Twilio WhatsApp sandbox. The same `ChatPipeline` powers both paths — messages are stored in `message_logs` and `st_turns` exactly as they would be from WhatsApp.

Twilio integration remains in the codebase (`POST /webhooks/twilio`) but is **optional until you are ready to demo on real WhatsApp**.

---

## Prerequisites

1. Supabase configured in `.env` (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`)
2. Schema applied: `make init-db`
3. API running: `make run`

Demo seed students:

| Tenant | Student phone | Name |
|--------|---------------|------|
| `tenant-demo-physics` | `94771234567` | Amaya Perera |
| `tenant-demo-chemistry` | `94779876543` | Kavindu Silva |

---

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/chat` | Send a student message → receive AI reply |
| `GET` | `/chat/turns` | Fetch conversation history for a session |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Send a message

```bash
curl -s http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-demo-physics",
    "phone": "94771234567",
    "message": "Hello, I want to join A/L Physics"
  }' | python3 -m json.tool
```

Example response:

```json
{
  "reply": "Thanks for messaging Demo Physics Academy! Axiom AI is connected and received your message. An agent will help you soon.",
  "tenant_id": "tenant-demo-physics",
  "tenant_slug": "demo-physics",
  "tenant_name": "Demo Physics Academy",
  "student_id": "stu-physics-001",
  "phone": "94771234567",
  "session_id": "tenant-demo-physics:94771234567",
  "student_registered": true
}
```

### Request body

| Field | Required | Description |
|-------|----------|-------------|
| `tenant_id` | Yes | Tuition agency tenant ID |
| `phone` | Yes | Student WhatsApp number (digits, no `+`) |
| `message` | Yes | Message text |
| `media_url` | No | Optional image URL (simulates bank-slip upload) |

---

## Fetch conversation history

```bash
curl -s "http://localhost:8000/chat/turns?tenant_id=tenant-demo-physics&phone=94771234567" \
  | python3 -m json.tool
```

Returns all turns in the session (`user` + `assistant` roles) from `st_turns`.

---

## Session model

Sessions are logical — no `chat_sessions` table. The session key is:

```
{tenant_id}:{phone}
```

Example: `tenant-demo-physics:94771234567`

Unknown phones auto-provision a stub `students` row (same behaviour as the Twilio path).

---

## Smoke test

```bash
make smoke-chat
```

Runs the pipeline in-process with mocked Supabase writes (no server needed).

---

## Twilio (later)

When you are ready for real WhatsApp:

1. Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` in `.env`
2. Set `TWILIO_WEBHOOK_URL` to your public URL + `/webhooks/twilio`
3. Set `MESSAGING_DRY_RUN=false`
4. Point Twilio sandbox webhook at your server

The Twilio webhook calls the same `ChatPipeline.process_twilio()` — no duplicate logic.

---

## Architecture

```
POST /chat  ──────────────┐
                          ├──► ChatPipeline.process_message()
POST /webhooks/twilio ────┘           │
                                      ├── IdentityResolver
                                      ├── MessagePersistence → message_logs, st_turns
                                      └── (Twilio only) TwilioMessagingClient
```

Phase 2 will replace the fixed reply inside `ChatPipeline` with `run_chat_turn()` (decision graph + agents).

---

## Related docs

- [DATABASE.md](DATABASE.md) — schema reference
- [AI Backend Roadmap](Technical%20Docs/AI%20backend%20-%20Roadmap.md) — phase plan
