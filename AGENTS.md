# AGENTS.md — Axiom AI Backend

Multi-tenant AI tutor backend (hackathon MVP). FastAPI + LangChain + Supabase + Qdrant.

## Quick Commands

```bash
make install    # pip install -r requirements.txt
make run        # uvicorn api.main:app --reload (port 8000)
make test       # pytest tests/ -v
make lint       # ruff check src tests scripts
make health     # curl localhost:8000/health
make init-db    # Run sql/01_schema.sql + sql/02_seed_demo.sql
make smoke-llm  # LLM connectivity test
```

No typecheck command exists yet — pyright is configured but no make target.

## Project Structure

- `src/api/` — FastAPI app entry point (`main.py`), routers, schemas, middleware
- `src/agents/prompts/` — LLM prompt templates
- `src/domain/` — Enums and domain models
- `src/infrastructure/config.py` — Central config loader (reads `config/*.yaml` + `.env`)
- `src/infrastructure/db/` — Supabase client
- `src/infrastructure/llm/` — LLM provider abstraction
- `src/infrastructure/observability.py` — Langfuse tracing
- `src/memory/` — Stub (Phase 2+)
- `src/services/` — Business logic
- `config/param.yaml` — Runtime parameters (non-secret)
- `config/models.yaml` — Model registry by provider/tier
- `sql/` — Schema (`01_schema.sql`) and seed data (`02_seed_demo.sql`)
- `scripts/` — Init, smoke test, verify utilities

## Environment

- `.env` (gitignored) holds all secrets — copy from `.env.example`
- Config loaded via `infrastructure/config.py`: YAML for parameters, env vars for secrets
- `PYTHONPATH` must be `src` (Makefile exports this)

## LLM Providers

Roles are mapped in `config/param.yaml` under `llm.roles`:
- **chat**: OpenAI gpt-4o-mini
- **merge**: Google Gemini 2.5 Flash
- **router/guardrail**: Groq llama-3.3-70b
- **extractor**: Groq llama-3.1-8b

Default provider: OpenRouter. Use `get_role_config(role)` to resolve model+provider.

## Testing

- pytest with `asyncio_mode = "auto"` — async tests run without decorators
- `pythonpath = ["src"]` in pyproject.toml means imports resolve from `src/`
- Run a single test: `python -m pytest tests/test_health.py -v`

## Linting

- Ruff: line-length 120, target Python 3.11
- Rules: E, F, W, I, N, UP, B, SIM
- Run on: `src tests scripts`

## Gotchas

- `.env` is loaded with `override=True` in `main.py` — env vars always win over defaults
- `DEV_TENANT_ID` env var is for local dev only, never use in production code paths
- `MESSAGING_DRY_RUN=true` by default — Twilio won't actually send messages
- Qdrant is optional until Phase 4 (RAG)
- Langfuse is optional — gracefully degrades if keys missing
- Dashboard is a separate repo (only a README placeholder here)
