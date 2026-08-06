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
                                      ├── run_chat_turn()  ← Phase 2
                                      │     ├── decision_graph (guardrail ∥ router → decide)
                                      │     └── orchestrator (direct + specialist stubs)
                                      ├── MessagePersistence → message_logs, st_turns
                                      └── (Twilio only) TwilioMessagingClient
```

### Reference implementations

Phase 2 modules are **ported from reference projects**, then adapted for the Axiom MVP SRS:

| Axiom module | Source project | Original file |
|---|---|---|
| `decision_graph.py`, `guardrail.py`, `router.py`, `decision_state.py`, `decision_bridge.py` | **BookMe AI** | `src/agents/decision_*.py`, `guardrail.py`, `router.py` |
| `chat_pipeline.py`, `orchestrator.py` | **BookMe AI** | `src/agents/chat_pipeline.py`, `orchestrator.py` |
| `memory_server.py`, `mcp_config.py`, `st_store.py` | **Week 13** | `src/mcp_servers/memory_server.py`, `memory/st_store.py` |
| `agent_prompts.py` | **BookMe AI** | `src/agents/prompts/agent_prompts.py` (tuition domain) |

When extending Phases 3–5, copy the corresponding CRM/Drive/RAG modules from Week 13 and specialist agent nodes from BookMe AI orchestrator patterns.

Set `AGENT_USE_MCP=true` in `.env` to route memory recall through the Week 13-style MCP subprocess.

---

## Phase 5 — Escalations + staff chat

> **Design rationale:** [PHASE5_DECISIONS.md](PHASE5_DECISIONS.md) · **API shapes:** [API_CONTRACT.md](API_CONTRACT.md)

### Staff chat (dashboard integration)

```bash
# Sidebar — list conversations
curl -s "http://localhost:8000/dashboard/chat/conversations?tenant_id=tenant-demo-physics"

# Thread for one student
curl -s "http://localhost:8000/dashboard/chat/conversations/94771234567?tenant_id=tenant-demo-physics"

# Staff reply
curl -s -X POST http://localhost:8000/dashboard/chat/send \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-demo-physics","phone":"94771234567","message":"We received your payment — welcome!"}'
```

### Escalations (payment + talk-to-tutor)

> **Design rationale:** [PHASE5_DECISIONS.md](PHASE5_DECISIONS.md) — why we use one escalation inbox instead of payments + human_mode.

Apply migration first: `make init-db` (includes `sql/02_phase5_escalations.sql`).

Re-seed Langfuse prompts: `make seed-langfuse`

### Flow 1 — Payment receipt → dashboard inbox

Complete admissions until you have a **pending enrollment**, then:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d @scripts/sample_requests/dashboard_payment_receipt.json
```

Staff dashboard:

```bash
# List open payment escalations
curl -s "http://localhost:8000/dashboard/escalations?tenant_id=tenant-demo-physics&reason_code=payment_receipt"

# Approve (activates enrollment + WhatsApp confirm)
curl -s -X PATCH "http://localhost:8000/dashboard/escalations/{id}/resolve?tenant_id=tenant-demo-physics"

# Reject (no enrollment + rejection WhatsApp)
curl -s -X PATCH "http://localhost:8000/dashboard/escalations/{id}/reject?tenant_id=tenant-demo-physics"
```

### Flow 2 — Talk to tutor

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d @scripts/sample_requests/dashboard_talk_to_tutor.json
```

Bot acknowledges and keeps chatting. Staff sees `reason_code=talk_to_tutor` in `/dashboard/escalations`.

### Staff reply

```bash
curl -s -X POST http://localhost:8000/dashboard/chat/send \
  -H "Content-Type: application/json" \
  -d @scripts/sample_requests/dashboard_staff_send.json
```

### Dashboard overview & chat logs

```bash
curl -s "http://localhost:8000/dashboard/overview?tenant_id=tenant-demo-physics"
curl -s "http://localhost:8000/dashboard/chat-logs?tenant_id=tenant-demo-physics&phone=94771234567"
```

Full API reference: [API_CONTRACT.md](API_CONTRACT.md)

---

## Related docs

- [PHASE5_DECISIONS.md](PHASE5_DECISIONS.md) — Phase 5 design decisions (escalation-only HITL)
- [API_CONTRACT.md](API_CONTRACT.md) — dashboard REST endpoints
- [DATABASE.md](DATABASE.md) — schema reference
- [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md) — Google Drive MCP setup, institute onboarding, testing
- [AI Backend Roadmap](Technical%20Docs/AI%20backend%20-%20Roadmap.md) — phase plan
