# Axiom AI - Dashboard Backend

FastAPI backend service powering the Axiom AI Staff Dashboard and managing Supabase database connections, payments, and class management.

## Prerequisites
- Python 3.10+
- Access to Supabase Project

## Setup Instructions

1. **Navigate to the Backend Directory:**
   ```bash
   cd Dashboard/backend

2. Setup vitual environment 
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

3. Run app
uvicorn app.main:app --reload --port 8000

View API Documentation:
Once running, access Swagger docs at: http://127.0.0.1:8000/docs