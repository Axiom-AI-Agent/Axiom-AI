.PHONY: install run test lint health ready config smoke-llm smoke-twilio smoke-chat verify-phase0 init-db

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

verify-phase0:
	$(PYTHON) scripts/verify_phase0.py

init-db:
	$(PYTHON) scripts/init_supabase.py
