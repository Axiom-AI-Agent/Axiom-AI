# Axiom AI — Backend

Multi-tenant AI backend for Sri Lankan private tuition (hackathon MVP).

## Quick start (Phase 0)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Apply sql/01_schema.sql + sql/02_seed_demo.sql in shared Supabase (or: make init-db)

make run
make test
```

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

See `docs/Technical Docs/AI backend - Roadmap.md` for the full implementation plan.
