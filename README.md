# Axiom AI

Multi-tenant AI tutor platform for Sri Lankan private tuition (hackathon MVP).

## Monorepo layout

```text
Axiom-AI/
├── AI-backend/          Multi-agent FastAPI backend, agents, MCP, RAG, demo chat UI
├── Dashboard/
│   ├── frontend/        Next.js staff dashboard (:3000)
│   └── backend/         FastAPI dashboard API (:8000)
└── LICENSE
```

## Quick start

### AI backend (multi-agent chat)

```bash
cd AI-backend
cp .env.example .env   # set OPENAI_API_KEY, SUPABASE_*, etc.
make venv && source .venv/bin/activate
make init-db
make run               # http://localhost:8000
```

Optional student demo UI:

```bash
cd AI-backend
make demo-ui           # http://localhost:5173
```

### Staff dashboard

**Backend** (terminal 1):

```bash
cd Dashboard/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Uses AI-backend/.env for SUPABASE_DB_URL (or set env vars directly)
uvicorn app.main:app --reload --port 8000
```

**Frontend** (terminal 2):

```bash
cd Dashboard/frontend
npm install
npm run dev            # http://localhost:3000
```

> **Port note:** AI backend and Dashboard backend both default to port 8000. Run only one at a time, or start Dashboard backend on another port and set `NEXT_PUBLIC_API_URL` in `Dashboard/frontend/.env.local`.

## Docs

- [AI-backend/README.md](AI-backend/README.md) — agents, MCP, smoke tests
- [AI-backend/docs/SETUP.md](AI-backend/docs/SETUP.md) — full setup guide
- [Dashboard/README.md](Dashboard/README.md) — staff dashboard
