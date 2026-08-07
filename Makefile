.PHONY: ai-backend dashboard-backend dashboard-frontend demo-ui

# Convenience targets from repo root — delegate to subprojects

ai-backend:
	$(MAKE) -C AI-backend run

ai-test:
	$(MAKE) -C AI-backend test

ai-install:
	$(MAKE) -C AI-backend install

dashboard-backend:
	cd Dashboard/backend && uvicorn app.main:app --reload --port 8001

dashboard-frontend:
	cd Dashboard/frontend && npm run dev

demo-ui:
	$(MAKE) -C AI-backend demo-ui
