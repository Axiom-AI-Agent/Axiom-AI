.PHONY: install venv run test lint health ready config smoke-llm smoke-twilio smoke-chat smoke-routing smoke-st-memory smoke-mcp-memory smoke-mcp-client smoke-admissions smoke-phase4 smoke-phase5-dashboard smoke-phase6 smoke-concurrent smoke-gates smoke-gates-phase6 smoke-langfuse seed-langfuse clear-demo-session check-python verify-phase0 init-db ingest-demo demo-ui-install demo-ui

# Prefer Python 3.11 when available (required for MCP packages mcp + langchain-mcp-adapters)
PYTHON ?= $(shell (command -v python3.11 >/dev/null 2>&1 && echo python3.11) || echo python3)
VENV_PY := $(shell (test -x .venv/bin/python && echo .venv/bin/python) || echo $(PYTHON))
export PYTHONPATH := src

venv:
	@if command -v python3.11 >/dev/null 2>&1; then \
		echo "Creating .venv with python3.11..."; \
		python3.11 -m venv .venv; \
	else \
		echo "WARN: python3.11 not found — using python3 (MCP packages need 3.10+)"; \
		python3 -m venv .venv; \
	fi
	.venv/bin/pip install -U pip
	.venv/bin/pip install -r requirements.txt
	@.venv/bin/python scripts/check_python.py || true

install:
	$(VENV_PY) -m pip install -U pip
	$(VENV_PY) -m pip install -r requirements.txt
	@$(VENV_PY) scripts/check_python.py || true

run:
	$(VENV_PY) -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(VENV_PY) -m pytest tests/ -v

lint:
	$(PYTHON) -m ruff check src tests scripts

health:
	curl -s http://localhost:8000/health | $(PYTHON) -m json.tool

ready:
	curl -s http://localhost:8000/ready | $(PYTHON) -m json.tool

config:
	curl -s http://localhost:8000/config | $(PYTHON) -m json.tool

smoke-llm:
	$(PYTHON) scripts/smoke_llm.py

smoke-twilio:
	$(PYTHON) scripts/smoke_twilio.py

smoke-chat:
	$(PYTHON) scripts/smoke_chat.py

smoke-routing:
	$(PYTHON) scripts/test_routing_smoke.py

smoke-st-memory:
	$(PYTHON) scripts/smoke_st_memory.py

smoke-mcp-memory:
	$(PYTHON) scripts/smoke_mcp_memory.py

smoke-mcp-client:
	$(VENV_PY) scripts/test_mcp_client.py

smoke-admissions:
	$(PYTHON) scripts/smoke_admissions.py

smoke-phase4:
	$(VENV_PY) scripts/smoke_phase4_e2e.py

smoke-phase4-live:
	$(VENV_PY) scripts/smoke_phase4_e2e.py --live-rag

ingest-demo:
	PYTHONPATH=src $(VENV_PY) scripts/ingest_tenant_notes.py --tenant-id tenant-demo-physics
	PYTHONPATH=src $(VENV_PY) scripts/ingest_tenant_notes.py --tenant-id tenant-demo-chemistry

smoke-gates: smoke-routing smoke-st-memory smoke-mcp-memory smoke-admissions smoke-phase4

smoke-phase5-dashboard:
	$(VENV_PY) scripts/smoke_phase5_dashboard.py

smoke-phase6:
	$(VENV_PY) scripts/smoke_phase6_e2e.py

smoke-phase6-oos:
	$(VENV_PY) scripts/smoke_phase6_e2e.py --scenario oos

smoke-concurrent:
	$(VENV_PY) scripts/smoke_concurrent_chat.py

smoke-gates-phase6: smoke-phase6 smoke-phase5-dashboard smoke-mcp-client smoke-langfuse smoke-concurrent

smoke-langfuse:
	$(PYTHON) scripts/smoke_langfuse_trace.py

seed-langfuse:
	$(PYTHON) scripts/seed_langfuse_prompts.py

clear-demo-session:
	$(PYTHON) scripts/clear_demo_session.py

check-python:
	$(PYTHON) scripts/check_python.py

verify-phase0:
	$(PYTHON) scripts/verify_phase0.py

init-db:
	$(PYTHON) scripts/init_supabase.py

demo-ui-install:
	cd demo-ui-org/student-chat && npm install

demo-ui:
	cd demo-ui-org/student-chat && npm run dev
