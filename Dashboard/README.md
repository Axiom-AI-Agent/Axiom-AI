# Axiom AI — Staff Dashboard

Staff dashboard for tuition centers: overview metrics, classes, payments, escalations, and message logs.

## Layout

```text
Dashboard/
├── frontend/    Next.js 16 + React 19 (:3000)
└── backend/     FastAPI + SQLAlchemy (:8000)
```

## Prerequisites

- Node 18+
- Python 3.10+
- Supabase project with schema applied (`make init-db` from `AI-backend/`)

## Backend

```bash
cd Dashboard/backend
python -m venv venv
source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Environment: loads `SUPABASE_DB_URL` from the first file found:

1. `Dashboard/backend/.env`
2. `AI-backend/.env` (shared monorepo config)
3. repo root `.env`

API docs: http://127.0.0.1:8000/docs

## Frontend

```bash
cd Dashboard/frontend
npm install
npm run dev
```

Open http://localhost:3000

Optional `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8000
```

## Build for production

```bash
cd Dashboard/frontend
npm run build
npm start
```
