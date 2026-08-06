# Phase 6 — Implementation Plan

**Objective:** Integration, E2E verification, observability audit, and handoff to dashboard + ops.

> **Scope (current):** Twilio live webhook and **Google Drive MCP** deferred. Gate uses `POST /chat`, MCP **crm + rag + memory** (`MCP_INCLUDE_DRIVE=false`), and [SETUP.md](SETUP.md).

**Duration:** ~1 day (8h)  
**Prerequisite:** Phase 5 complete ([PHASE5_DECISIONS.md](PHASE5_DECISIONS.md), [API_CONTRACT.md](API_CONTRACT.md))  
**Roadmap reference:** [AI backend - Roadmap § Phase 6](Technical%20Docs/AI%20backend%20-%20Roadmap.md)

---

## Starting point (what’s already done)

| Area | Status |
|------|--------|
| All specialist nodes wired in orchestrator | ✅ admissions, resource, payment_check, escalation, direct, merge |
| Dashboard REST APIs + tenant scoping | ✅ |
| Unit/integration tests | ✅ 134 passing (`make test`) |
| Per-phase smoke scripts | ✅ phases 1–4 + admissions + langfuse |
| Langfuse `@observe` on router, guardrail, orchestrator nodes, tools | ✅ |
| MCP server config (crm, drive, rag, memory) | ✅ `mcp_config.py` |
| Prompt local fallbacks + `seed-langfuse` script | ✅ |
| **Phase 6 E2E bundle** | ✅ `make smoke-phase6` |
| **MCP lifespan in FastAPI** | ✅ BookMe `main.py` pattern |
| **`docs/SETUP.md`** | ✅ |
| **Concurrent webhook perf smoke** | ✅ `make smoke-concurrent` (HTTP /chat) |
| **Dashboard handoff checklist** | ✅ in SETUP.md §9 |

---

## Workstreams

### WS1 — MCP lifecycle & orchestrator hardening (~1.5h)

**Goal:** All four MCP servers start reliably under the API process; `/ready` reflects MCP health.

| Task | File(s) | Done when |
|------|---------|-----------|
| Preload MCP client in FastAPI `lifespan` when `AGENT_USE_MCP=true` | `src/api/main.py`, `src/agents/runtime.py` | First `/chat` request does not cold-start subprocesses |
| Shutdown: close MCP sessions on app exit | `lifespan` yield teardown | No zombie child processes after `uvicorn` stop |
| Add `/ready` check: `mcp_servers` (4/4 reachable or degraded detail) | `src/api/routers/health.py` | Ready report lists crm/drive/rag/memory |
| Verify `build_agent_mcp()` path in CI/local with Python 3.11 | manual + test | `make smoke-mcp-memory` passes with `AGENT_USE_MCP=true` |
| Document fallback: `AGENT_USE_MCP=false` + `ALLOW_INPROCESS_TOOLS=true` | SETUP.md | Dev without MCP still works |

**Acceptance:** E2E harness runs with MCP enabled; `/ready` shows MCP status.

---

### WS2 — Five E2E smoke scenarios (~2.5h)

**Goal:** Five scripted flows the team can run before demo day — mirror roadmap acceptance criteria.

Create **`scripts/smoke_phase6_e2e.py`** (orchestrator + HTTP, mock-friendly) and **`make smoke-phase6`**.

| # | Scenario | Trigger | Assert |
|---|----------|---------|--------|
| 1 | **Onboarding** | Multi-turn admissions via `POST /chat` | Pending enrollment created; consent + class slots captured |
| 2 | **Resource** | "Send me the 2023 physics paper" | Routes to resource; drive and/or RAG tool invoked; non-empty reply |
| 3 | **Payment** | `POST /chat` with `media_url` after pending enrollment | Escalation row `payment_receipt`; student ack mentions verification |
| 4 | **Escalation** | "Can I speak to sir?" | Escalation row `talk_to_tutor`; ack mentions tutor notified |
| 5 | **Off-topic** | "What's the weather?" | Guardrail/OOS path; no CRM write; polite redirect |

**Implementation notes:**

- Reuse patterns from `smoke_admissions.py`, `smoke_phase4_e2e.py`, `smoke_st_memory.py`.
- Use unique phone per run (`9477099{timestamp}`) to avoid stale DB state.
- Mock LLM optional flag (`--mock-llm`) for CI without keys; live mode when `OPENAI_API_KEY` set.
- Add **`scripts/smoke_phase5_dashboard.py`**: list escalations → resolve payment → staff chat send (HTTP only, mocked Supabase optional).

**Also add pytest wrappers** (fast, mocked) in `tests/test_e2e_smoke.py` so `make test` covers wiring without live LLM.

**Acceptance:** `make smoke-phase6` exits 0 locally with `.env` configured.

---

### WS3 — Dashboard integration smoke (~1h)

**Goal:** Prove staff API contract end-to-end against real Supabase (optional skip without DB).

| Step | API |
|------|-----|
| Overview counts | `GET /dashboard/overview?tenant_id=` |
| List inbox after payment chat | `GET /dashboard/escalations?reason_code=payment_receipt` |
| Open thread | `GET /dashboard/chat/conversations/{phone}` |
| Staff reply | `POST /dashboard/chat/send` |
| Resolve payment | `PATCH /dashboard/escalations/{id}/resolve` |

Document curl block in [DEV_CHAT.md](DEV_CHAT.md) § Phase 6 handoff.

**Acceptance:** Single script or documented manual run completes without 4xx/5xx.

---

### WS4 — Observability & prompts (~1.5h)

**Goal:** Langfuse traces visible per tenant/session/user; prompts promoted to `production`.

| Task | Detail |
|------|--------|
| Run each E2E scenario with Langfuse keys | Confirm trace tree: `chat_turn` → router → node → tool |
| Extend `scripts/smoke_langfuse_trace.py` | Print trace URL / id; assert `tenant_id` + `session_id` tags |
| Run `make seed-langfuse` | All prompts in [agent_prompts.py](../src/agents/prompts/agent_prompts.py) catalog uploaded |
| Document promote workflow | staging label → test → promote to `production` in SETUP.md |
| Audit missing `@observe` | decision_graph nodes, CRM MCP calls if gaps found |

**Acceptance:** Sample trace link attached in SETUP.md; seed script idempotent.

---

### WS5 — Error handling audit (~1h)

**Goal:** Failures degrade gracefully; no silent cross-tenant leaks.

| Check | Expected behaviour |
|-------|-------------------|
| Router LLM timeout / parse error | Fallback route `direct` or safe message |
| Guardrail LLM failure | Fail-open (allow message through with log) |
| MCP subprocess crash mid-request | Clear 503 or in-process fallback per `ALLOW_INPROCESS_TOOLS` |
| Missing Qdrant / Drive creds | Resource agent returns helpful message, not stack trace |
| Invalid tenant on dashboard | 404/403 (already implemented) |
| Payment with no pending enrollment | Agent error message, no orphan escalation |

Add or extend tests in `tests/test_runtime_mcp_fallback.py`, `tests/test_heuristic_router.py`.

**Acceptance:** Checklist signed off in this doc; no unhandled exceptions in E2E runs.

---

### WS6 — `docs/SETUP.md` (~1.5h)

**Goal:** Single onboarding doc for hackathon deploy + dashboard handoff.

**Sections:**

1. **Prerequisites** — Python 3.11, Supabase project, optional Twilio/Qdrant/Drive/Langfuse
2. **Clone & env** — `.env.example` field-by-field
3. **Database** — `make init-db`, seed verification
4. **Langfuse** — `make seed-langfuse`, label workflow
5. **Qdrant RAG** — `make ingest-demo`, collection naming
6. **Google Drive** — link to [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md)
7. **Twilio sandbox** — join code, webhook URL, `MESSAGING_DRY_RUN`
8. **Run & verify** — `make run`, `make test`, `make smoke-phase6`
9. **Dashboard team** — [API_CONTRACT.md](API_CONTRACT.md), `X-Tenant-ID`, shared Supabase RLS note
10. **Troubleshooting** — MCP, Langfuse auth, Supabase connection

Update [README.md](../README.md) to link SETUP.md prominently.

**Acceptance:** New developer can go from clone → working `/chat` in <30 min following SETUP.md.

---

### WS7 — Performance smoke (~0.5h)

**Goal:** 10 concurrent inbound messages without errors or reply mixing.

Create **`scripts/smoke_concurrent_chat.py`**:

- 10 parallel `POST /chat` (or `/webhooks/twilio` with dry-run) with distinct phones
- Assert all 200, distinct `session_id`s, p95 latency logged
- Optional: add to `make smoke-phase6` as `--perf` flag

**Acceptance:** Script completes; no shared session bleed (verify via unique session_ids).

---

## Suggested schedule (1 day)

| Block | Workstream |
|-------|------------|
| Hour 1 | WS1 MCP lifespan + `/ready` |
| Hour 2–3 | WS2 E2E scripts (scenarios 1–3) |
| Hour 4 | WS2 E2E scripts (4–5) + WS3 dashboard smoke |
| Hour 5 | WS4 Langfuse audit + seed |
| Hour 6 | WS5 error audit + tests |
| Hour 7 | WS6 SETUP.md |
| Hour 8 | WS7 perf smoke + roadmap checkbox update + handoff email to dashboard team |

---

## Acceptance criteria mapping

| Roadmap criterion | How we close it |
|-------------------|-----------------|
| 5 E2E scripts pass | `make smoke-phase6` (5 scenarios) |
| `make test` green | Maintain 134+; add mocked E2E tests |
| Langfuse traces per tenant/session/user | WS4 smoke + SETUP screenshot/link |
| Prompts versioned with `production` label | `make seed-langfuse` + promote docs |
| SETUP.md + API_CONTRACT.md complete | WS6; API_CONTRACT already done |
| Dashboard team confirms API access | WS3 handoff checklist (manual sign-off) |
| All four MCP servers in E2E harness | WS1 + `smoke-mcp-memory` in phase6 gate |

---

## Makefile targets (to add)

```makefile
smoke-phase5-dashboard:
	$(VENV_PY) scripts/smoke_phase5_dashboard.py

smoke-phase6:
	$(VENV_PY) scripts/smoke_phase6_e2e.py

smoke-phase6-live:
	$(VENV_PY) scripts/smoke_phase6_e2e.py --live

smoke-concurrent:
	$(VENV_PY) scripts/smoke_concurrent_chat.py

smoke-gates-phase6: smoke-phase6 smoke-phase5-dashboard smoke-langfuse smoke-concurrent
```

---

## Explicitly out of scope (stay V2)

- Production Twilio / Meta WhatsApp Business API
- Redis, Celery, worker processes
- Full Supabase Auth on backend (dashboard frontend owns JWT + RLS)
- `human_mode` / staff bot mute
- OCR payment verification
- SSE streaming chat (BookMe pattern — not needed for WhatsApp MVP)

---

## Handoff checklist (dashboard team)

- [ ] Received [API_CONTRACT.md](API_CONTRACT.md)
- [ ] `SUPABASE_URL` + anon key for frontend; service key stays backend-only
- [ ] `X-Tenant-ID` header wired from staff session
- [ ] Escalation inbox + chat UI pointed at `/dashboard/*`
- [ ] Confirmed test tenant: `tenant-demo-physics`
- [ ] Joined Twilio sandbox (if testing live WhatsApp)

---

## Risk register

| Risk | Mitigation |
|------|------------|
| MCP flaky on Python 3.9 | Require 3.11 in SETUP; default `AGENT_USE_MCP=false` in CI |
| Live LLM costs during E2E | `--mock-llm` mode; heuristic assertions on route/intent |
| Demo student already enrolled | E2E uses fresh phone or `clear-demo-session` script |
| Langfuse keys missing | Skip trace assertions; local prompt fallbacks already work |

---

*Plan created at Phase 5 completion — update checkboxes in roadmap § Phase 6 as work lands.*
