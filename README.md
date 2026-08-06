# Axiom AI — Backend

Multi-tenant AI backend for Sri Lankan private tuition (hackathon MVP).

## Quick start

**Requires Python 3.10+** (3.11 recommended). MCP subprocess servers (`mcp`, `langchain-mcp-adapters`) do not install on Python 3.9.

```bash
# Recommended — recreate venv with Python 3.11 (you have it at ~/.local/bin/python3.11)
rm -rf .venv
make venv
source .venv/bin/activate

cp .env.example .env
# Set OPENAI_API_KEY, QDRANT_*, SUPABASE_*; use AGENT_USE_MCP=true only on Python 3.10+

make run
make test
```

If you must stay on Python 3.9 temporarily:

```bash
pip install -r requirements.txt   # MCP lines are skipped automatically
# In .env:
AGENT_USE_MCP=false
```

The app falls back to in-process tools when MCP is unavailable (`src/agents/runtime.py`).

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Docs

- [demo-ui-org/README.md](demo-ui-org/README.md) — WhatsApp student chat demo UI (`make demo-ui`)
- [SETUP.md](docs/SETUP.md) — install, env, Phase 6 verification gate
- [FINALIZE_CHECKLIST.md](docs/FINALIZE_CHECKLIST.md) — master MVP + Drive MCP + Telegram sign-off list
- [DEV_CHAT.md](docs/DEV_CHAT.md) — local `/chat` testing (no Twilio)
- [DRIVE_INTEGRATION.md](docs/DRIVE_INTEGRATION.md) — Google Drive MCP, institute onboarding, testing
- [DATABASE.md](docs/DATABASE.md) — Supabase schema
- [AI Backend Roadmap](docs/Technical%20Docs/AI%20backend%20-%20Roadmap.md) — full implementation plan
