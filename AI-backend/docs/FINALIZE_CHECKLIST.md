# Axiom AI Backend — Finalize Checklist

Master list to close the hackathon MVP and add **Google Drive MCP** + **Telegram Bot** integrations.

**Last updated:** Phase 6 + institute-info CRM + routing fixes.

Use this doc for demo-day sign-off. Check items as you complete them.

---

## How to use

| Priority | Meaning |
|----------|---------|
| **P0** | Must pass before calling the backend “done” for hackathon |
| **P1** | Strongly recommended for a polished demo |
| **P2** | New integration work (Drive MCP live, Telegram) |
| **V2** | Explicitly deferred — do not block MVP on these |

**Verification gate (when P0 is ready):**

```bash
make test
make smoke-gates-phase6    # needs OPENAI + Supabase (+ Langfuse optional)
make smoke-phase4-live     # needs Qdrant + ingest
```

---

## P0 — Must finalize (MVP gate)

### Core agent & routing

- [x] **Restart backend** after latest changes (`make run`) — onboarding + institute-info routing
- [x] **Onboarding flow** — enroll intent, name/school/district slots, class pick, YES confirm, pending enrollment in DB
- [x] **Enrollment status** — “Am I enrolled?” answered correctly (registered vs visitor)
- [x] **Institute info (CRM)** — “What classes are available?”, fees, tutor/staff, centre details → DB via `get_tenant_info` / `list_classes` / `list_staff` (not resource agent)
- [x] **Tutoring questions** — “Explain velocity from tutor notes” → resource/RAG (not onboarding)
- [x] **Off-topic guardrail** — weather/trivia blocked politely
- [x] **Escalation** — “Speak to tutor” creates `talk_to_tutor` escalation row
- [x] **Payment slip** — image/`media_url` after pending enrollment → `payment_receipt` escalation

### Live infrastructure

- [x] **Supabase** — `make init-db`, demo tenant `tenant-demo-physics` seeded
- [x] **Environment** — `.env` complete: `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- [x] **MCP lifecycle** — `AGENT_USE_MCP=true`; `/ready` shows crm + rag + memory healthy
- [x] **MCP fallback** — `ALLOW_INPROCESS_TOOLS=true` documented if subprocess fails

### RAG (tutor notes)

- [x] **Qdrant** — `QDRANT_URL` + `QDRANT_API_KEY` set
- [x] **Ingest** — `make ingest-demo` for demo tenants
- [x] **Live resource smoke** — `make smoke-phase4-live` passes for enrolled student
- [x] **Enrolled-only gate** — unenrolled users get clear “join class” message for RAG/Drive content

### Phase 6 E2E scripts

- [x] `make smoke-phase6` — all 5 scenarios pass (onboarding, resource, payment, escalation, OOS)
- [x] `make smoke-phase5-dashboard` — dashboard API contract
- [x] `make smoke-mcp-client` — crm + rag + memory tools
- [x] `make smoke-concurrent` — 10 parallel `/chat` sessions, no session bleed
- [x] `make test` — green (160+ tests)

### Langfuse

- [x] `make seed-langfuse` — all prompts uploaded (router, guardrail, direct, merge, stubs)
- [ ] **Promote** staging → `production` in Langfuse UI *(seeded with `production` label; confirm in UI)*
- [x] `make smoke-langfuse` — trace id printed; tags include `tenant_id`, `session_id`
- [x] Sample trace link saved for handoff / demo backup — `29f237a0dc037f23eb55d6ba814b39c6` @ https://us.cloud.langfuse.com

### Dashboard handoff

- [x] Dashboard team has [API_CONTRACT.md](API_CONTRACT.md)
- [x] `X-Tenant-ID: tenant-demo-physics` on all dashboard calls
- [x] Escalation inbox → `GET /dashboard/escalations`
- [x] Staff chat → conversations + send
- [x] Payment resolve → `PATCH /dashboard/escalations/{id}/resolve`
- [ ] Frontend uses Supabase **anon** key; service key stays on AI backend only *(frontend-owned)*

### Error handling (Phase 6 WS5)

- [x] Router LLM failure → safe `direct` fallback
- [x] Guardrail LLM failure → fail-open with log
- [x] MCP crash mid-request → 503 or in-process fallback (no stack trace to user)
- [x] Missing Qdrant → helpful resource message
- [x] Payment with no pending enrollment → clear error, no orphan escalation

---

## P1 — Demo polish

### Demo UI (`demo-ui-org/`)

- [ ] Student chat runs — `make demo-ui-install && make demo-ui`
- [ ] Quick actions aligned with backend (join class, class list, explain topic, payment slip)
- [ ] **Staff console** (optional) — thin pane: escalation inbox + approve/reject + staff reply
- [ ] Demo script walkthrough — [demo-ui-org/DEMO_SCRIPT.md](../demo-ui-org/DEMO_SCRIPT.md)

### Tests & smoke gaps

- [ ] Add **institute-info** scenario to `scripts/smoke_phase6_e2e.py` (“what classes are available”)
- [ ] Re-run admissions + onboarding route-lock tests after prompt changes

### Documentation sync

- [ ] Update roadmap Phase 6 checkboxes in [AI backend - Roadmap.md](Technical%20Docs/AI%20backend%20-%20Roadmap.md)
- [ ] [SETUP.md](SETUP.md) reflects current env defaults and troubleshooting
- [ ] [PHASE6_PLAN.md](PHASE6_PLAN.md) workstreams signed off

### Twilio sandbox (optional for MVP)

- [ ] Twilio sandbox joined; webhook URL points to backend (or ngrok)
- [ ] `MESSAGING_DRY_RUN=false` for live send test
- [ ] `make smoke-twilio` passes

---

## P2 — Google Drive MCP integration

> **Current state:** Code exists (`drive_server.py`, `DriveTool`, resource agent drive path).  
> **Default:** `MCP_INCLUDE_DRIVE=false` — Drive MCP subprocess not started; mock/in-process fallback.

### Platform setup (once per deploy)

- [ ] Google Cloud project + **Drive API** enabled
- [ ] Service account created; JSON key on server (`GOOGLE_SERVICE_ACCOUNT_JSON`)
- [ ] Service account email shared on institute Drive root folder (Viewer)
- [ ] `.env`: `DRIVE_MOCK=false`, `GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/key.json`

### Per-tenant onboarding

- [ ] Institute creates Drive layout: `{root}/{Exact class name}/papers|tutes|textbooks|syllabus`
- [ ] `tenants.drive_folder_id` set in Supabase for each tenant (seed + production)
- [ ] Upload demo PDFs for `tenant-demo-physics` past-paper smoke

### Enable Drive MCP in runtime

- [ ] Set `MCP_INCLUDE_DRIVE=true` in `.env`
- [ ] Confirm `axiom-drive` in `build_mcp_server_config()` starts at API lifespan
- [ ] `/ready` reports drive MCP tools: `drive_search`, `drive_list`
- [ ] Add drive tools to `MCP_CORE_TOOL_NAMES` or document as optional fourth server
- [ ] `make smoke-mcp-client` includes drive tool invocation

### Resource agent path

- [ ] “Send me 2023 Physics past paper” routes to **resource** → **drive** sub-path
- [ ] MCP `drive_search` returns tenant-scoped file links (not cross-tenant)
- [ ] `DRIVE_MOCK=true` dev path still works when Google creds absent
- [ ] Error message when folder empty or API fails (no stack trace)

### Testing & docs

- [ ] Follow [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md) smoke steps end-to-end
- [ ] Add drive scenario to phase6 E2E (or `make smoke-resource` with live Drive)
- [ ] Tenant isolation test — tenant A cannot list tenant B files

**Key files:**

| Area | Path |
|------|------|
| MCP server | `src/mcp_servers/drive_server.py` |
| MCP config | `src/mcp_servers/mcp_config.py` |
| Tool logic | `src/agents/tools/drive_tool.py` |
| Google client | `src/services/drive_service/drive_client.py` |
| Debug REST | `src/api/routers/tools/drive.py` |
| Resource agent | `src/agents/nodes/resource_agent.py` |

---

## P2 — Telegram Bot integration

> **Current state:** `chat_channel` enum includes `telegram`; **no webhook, parser, or send client implemented.**  
> Reference pattern: Twilio webhook + `ChatPipeline`.

### Bot & environment

- [ ] Create bot via [@BotFather](https://t.me/BotFather); store `TELEGRAM_BOT_TOKEN`
- [ ] Optional per-tenant token column or config (multi-tenant SaaS) — MVP: single demo bot
- [ ] `.env.example` + [SETUP.md](SETUP.md): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`
- [ ] Set webhook URL: `POST https://api.telegram.org/bot<token>/setWebhook`

### Inbound webhook

- [ ] New router: `src/api/webhooks/telegram.py` → `POST /webhooks/telegram`
- [ ] Parse Telegram `Update` JSON (text, photo/document for payment slips)
- [ ] Map `chat.id` / `from.id` → identity key (phone optional; use `telegram_user_id` in resolver)
- [ ] Validate webhook secret / optional signature
- [ ] Background task pattern (same as Twilio) — respond 200 within Telegram timeout
- [ ] Register router in `src/api/main.py`

### Outbound messaging

- [ ] `TelegramMessagingClient` — send text (+ photo for staff replies if needed)
- [ ] Integrate with `ChatPipeline._deliver_reply` (channel-aware: Twilio vs Telegram vs dry-run)
- [ ] `MESSAGING_DRY_RUN=true` logs outbound without sending

### Identity & persistence

- [ ] Extend `IdentityResolver` — resolve student by Telegram user id (new lookup or map to phone)
- [ ] Schema consideration: `students.telegram_id` or mapping table (migration if needed)
- [ ] `InboundMessage.channel = ChatChannel.TELEGRAM`
- [ ] `message_logs` + `st_turns` store correct channel

### Agent pipeline

- [ ] Reuse existing `run_chat_turn` — no agent changes required if identity resolves
- [ ] Payment slip: Telegram photo → download file → `media_url` or stored ref for escalation
- [ ] Langfuse metadata tag `channel:telegram`

### Testing

- [ ] Unit tests: Telegram update parser, identity mapping
- [ ] `tests/test_telegram_webhook.py` — dry-run pipeline + mock Bot API
- [ ] `scripts/smoke_telegram.py` — optional live send (like `smoke_twilio.py`)
- [ ] Document local testing with ngrok + BotFather webhook

### Documentation

- [ ] New doc: `docs/TELEGRAM_INTEGRATION.md` (BotFather setup, webhook, env, smoke)
- [ ] Update [API main](README.md) webhook list
- [ ] SRS alignment note — Telegram as secondary channel (NFR-RE-04 failover = V2)

**Suggested file layout:**

```text
src/api/webhooks/telegram.py
src/services/messaging/telegram_client.py
src/services/messaging/parser.py          # parse_telegram_update()
src/services/identity/resolver.py       # telegram user lookup
sql/00d_students_telegram_id.sql          # optional migration
tests/test_telegram_webhook.py
scripts/smoke_telegram.py
```

---

## V2 — Out of scope (do not block MVP)

| Item | Notes |
|------|--------|
| Meta WhatsApp Cloud API (production) | Twilio sandbox / `POST /chat` for hackathon |
| Payment OCR / auto-verify | Staff approves via escalation |
| `human_mode` / bot mute during staff takeover | [PHASE5_DECISIONS.md](PHASE5_DECISIONS.md) |
| Long-term / episodic memory (LT) | ST memory (`st_turns`) only in MVP |
| Redis queue + background workers | Sync/background_tasks pattern today |
| PayHere / billing automation | Escalation-only payments |
| CAG / CRAG in decision graph | V2.1+ |
| Multi-route fan-out merge for every compound message | Gemini merge exists; full fan-out V2 |
| Production deploy / CI/CD | Host + secrets management |
| `make typecheck` (pyright) | Config exists; no Makefile target yet |
| WhatsApp → Telegram failover routing | V2 (NFR-RE-04) |

---

## Sign-off matrix

| Area | Owner | Done | Verified by |
|------|-------|------|-------------|
| P0 MVP gate | Backend | [x] | smoke-gates + live chat |
| RAG live | Backend | [x] | smoke-phase4-live |
| Langfuse | Backend | [x] | seed + smoke (confirm promote in UI) |
| Dashboard APIs | Backend + Frontend | [x] | smoke-phase5-dashboard |
| Demo UI student chat | Frontend | [ ] | |
| Google Drive MCP live | Backend | [ ] | |
| Telegram bot | Backend | [ ] | |
| Twilio sandbox (optional) | Backend | [ ] | |

---

## Quick reference — make targets

```bash
make run                  # API on :8000
make test                 # unit + mocked e2e
make init-db              # schema + seed
make ingest-demo          # Qdrant tutor notes
make seed-langfuse        # upload prompts

make smoke-phase6         # 5 live E2E scenarios
make smoke-phase5-dashboard
make smoke-mcp-client
make smoke-concurrent
make smoke-langfuse
make smoke-phase4-live    # RAG live
make smoke-gates-phase6   # full Phase 6 gate

make demo-ui              # student WhatsApp mock
```

---

## Related docs

- [SETUP.md](SETUP.md) — install & env
- [PHASE6_PLAN.md](PHASE6_PLAN.md) — Phase 6 workstreams
- [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md) — Drive MCP detail
- [API_CONTRACT.md](API_CONTRACT.md) — dashboard REST
- [DEV_CHAT.md](DEV_CHAT.md) — HTTP chat without Twilio/Telegram
- [demo-ui-org/DEMO_SCRIPT.md](../demo-ui-org/DEMO_SCRIPT.md) — presenter script
