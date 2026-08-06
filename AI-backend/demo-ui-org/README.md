# Demo UI — WhatsApp Student Chat

WhatsApp-style chat mock for **Demo Physics Academy**. Talks to the existing Axiom backend via `POST /chat` and `GET /chat/turns` — no Twilio, no auth, no staff dashboard in this UI.

## Quick start

```bash
# Terminal 1 — API (from AI-backend/)
cd AI-backend && make run

# Terminal 2 — demo UI
cd AI-backend && make demo-ui
```

Open http://localhost:5173

## Prerequisites

- Node 18+
- Backend on `:8000` (`make run`)
- DB seeded: `make init-db`
- `OPENAI_API_KEY` in `.env` for live agent replies
- Optional RAG: `make ingest-demo` before “Explain velocity” demo

## Features

- WhatsApp look (green user bubbles, white bot bubbles, DPA header)
- **Reset demo** — new phone `9477099XXXX` per session (avoids stale enrollments)
- Quick-action chips for live demos
- One-tap **payment slip** attach (`media_url` → backend)
- Lifecycle checklist (client-side heuristics)
- Vite proxy `/api` → `http://localhost:8000`

## Project layout

```text
demo-ui-org/
├── shared/           # tenant id, lifecycle steps, quick actions
├── student-chat/     # Vite + React SPA
├── DEMO_SCRIPT.md    # 5-minute presenter walkthrough
└── README.md
```

## Env (optional)

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_URL` | (dev proxy) | Production build — absolute API origin |

## Build

```bash
cd demo-ui-org/student-chat && npm run build
```

Output: `demo-ui-org/student-chat/dist/`
