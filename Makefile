.PHONY: install run test lint health ready config smoke-llm smoke-twilio smoke-chat smoke-routing smoke-st-memory smoke-mcp-memory smoke-admissions smoke-gates smoke-langfuse seed-langfuse clear-demo-session check-python verify-phase0 init-db

PYTHON ?= python3
export PYTHONPATH := src

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON) -m pytest tests/ -v

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

smoke-admissions:
	$(PYTHON) scripts/smoke_admissions.py

smoke-gates: smoke-routing smoke-st-memory smoke-mcp-memory smoke-admissions

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
