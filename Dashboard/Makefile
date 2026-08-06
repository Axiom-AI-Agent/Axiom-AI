.PHONY: backend frontend install-backend install-frontend dev

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

dev:
	@echo "Start backend and frontend in separate terminals:"
	@echo "  make backend   # http://localhost:8000"
	@echo "  make frontend  # http://localhost:3000"
