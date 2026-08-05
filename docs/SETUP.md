# Axiom AI — Setup Guide (Phase 6)

Get from clone to a working **`POST /chat`** and dashboard APIs. Patterns follow **BookMe AI** (`api/main.py` lifespan) and **Week 13** (MCP config, health probes).

**Deferred for now (not required for Phase 6 gate):**
- Twilio WhatsApp live webhook — use **`POST /chat`** instead ([DEV_CHAT.md](DEV_CHAT.md))
- Google Drive MCP subprocess — set `MCP_INCLUDE_DRIVE=false`; resource agent uses in-process `DriveTool` mock or [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md) later

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|--------|
| **Python 3.11** | Required for `langchain-mcp-adapters` + MCP stdio servers |
| **Supabase project** | Shared with dashboard team |
| **OpenAI API key** | Router, guardrail, chat (`gpt-4o-mini`) |
| **Google API key** | Optional — Gemini merge model |
| **Qdrant Cloud** | Optional until RAG live tests |
| **Langfuse** | Optional — local prompt fallbacks work offline |

---

## 2. Clone and virtualenv

```bash
git clone <repo>
cd Axiom-AI
cp .env.example .env
make venv
source .venv/bin/activate
```

---

## 3. Environment (`.env`)

### Required for live chat

```bash
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_DB_URL=postgresql://...   # for make init-db / schema tests
```

### Agent runtime (Phase 6 defaults)

```bash
AGENT_USE_MCP=true          # crm + rag + memory MCP servers at startup
MCP_INCLUDE_DRIVE=false     # Drive MCP deferred — in-process DriveTool fallback
ALLOW_INPROCESS_TOOLS=true  # fallback if MCP subprocess fails (local dev)
MESSAGING_DRY_RUN=true      # no Twilio sends; staff send still persists turns
DEV_TENANT_ID=tenant-demo-physics
```

### Optional

```bash
QDRANT_URL=
QDRANT_API_KEY=
GOOGLE_API_KEY=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PROMPT_LABEL=production
DRIVE_MOCK=true
```

---

## 4. Database

```bash
make init-db
```

Verify (optional, needs `SUPABASE_DB_URL`):

```bash
pytest tests/test_schema.py -v
```

Demo tenant: **`tenant-demo-physics`**

---

## 5. Langfuse prompts

```bash
make seed-langfuse
```

**Promote workflow (hackathon):**

1. Seed uploads prompts with label from `LANGFUSE_PROMPT_LABEL` (default `production`)
2. For staging tests: set `LANGFUSE_PROMPT_LABEL=staging`, seed, test, then promote in Langfuse UI → **Promote to production**
3. Local dev without keys uses fallbacks in `src/agents/prompts/tutoring_prompts.py`

---

## 6. RAG ingest (optional)

```bash
make ingest-demo
```

Then live resource smoke:

```bash
make smoke-phase4-live
```

---

## 7. Run the API

```bash
make run
```

Startup (BookMe pattern) preloads:

- Decision graph
- Orchestrator (+ MCP when `AGENT_USE_MCP=true`)
- Langfuse prompt cache

Check:

```bash
make health    # phase 6
make ready     # supabase + mcp tool probe
make config
```

Open docs: http://localhost:8000/docs

---

## 8. Verify (Phase 6 gate)

```bash
make test                      # unit + mocked e2e
make smoke-mcp-client          # crm + rag + memory MCP tools
make smoke-phase5-dashboard    # dashboard API contract
make smoke-phase6              # 5 live E2E scenarios (needs OPENAI + Supabase)
make smoke-concurrent          # 10 parallel /chat sessions
make smoke-langfuse            # trace id printed (needs Langfuse keys)
```

Single scenario:

```bash
make smoke-phase6-oos
```

Dev chat (no Twilio):

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-demo-physics","phone":"94771234567","message":"Hello"}'
```

See [DEV_CHAT.md](DEV_CHAT.md) for full examples.

---

## 9. Dashboard team handoff

| Doc | Purpose |
|-----|---------|
| [API_CONTRACT.md](API_CONTRACT.md) | All `/dashboard/*` endpoints |
| [PHASE5_DECISIONS.md](PHASE5_DECISIONS.md) | Escalation-only HITL rationale |

**Integration checklist:**

- [ ] Send `X-Tenant-ID: tenant-demo-physics` (or `?tenant_id=`) on every dashboard call
- [ ] Escalation inbox → `/dashboard/escalations`
- [ ] Staff chat → `/dashboard/chat/conversations` + `/send`
- [ ] Frontend Supabase anon key + RLS (service key stays on AI backend only)

---

## 10. Troubleshooting

| Symptom | Fix |
|---------|-----|
| MCP fails at startup | Python 3.11+, `pip install -r requirements.txt`; or `AGENT_USE_MCP=false` |
| `/ready` mcp check fails | Run `make smoke-mcp-client`; ensure `MCP_INCLUDE_DRIVE=false` unless Drive MCP intended |
| Empty RAG answers | `make ingest-demo`; set Qdrant env vars |
| Langfuse 401 | Check keys; set `LANGFUSE_ENABLED=false` for offline dev |
| Payment E2E fails | Student needs **pending enrollment** — run onboarding turns first |

---

## Related docs

- [DEV_CHAT.md](DEV_CHAT.md) — HTTP chat simulator
- [PHASE6_PLAN.md](PHASE6_PLAN.md) — implementation plan
- [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md) — when enabling Drive MCP
- [DATABASE.md](DATABASE.md) — schema reference
