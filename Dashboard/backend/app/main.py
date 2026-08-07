from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routes import (
    auth,
    classes,
    payments,
    students,
    message_logs,
    escalations,
    escalation_websocket,
    invoices,
    dashboard,
    tenant,
)
from app.database.session import engine, Base

import app.models  

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Axiom AI API")

frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000",
)

allowed_origins = [
    "http://localhost:3000",
]

if frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(payments.router)
app.include_router(students.router)
app.include_router(message_logs.router)
app.include_router(escalations.router)
app.include_router(invoices.router)
app.include_router(dashboard.router)
app.include_router(tenant.router)
app.include_router(escalation_websocket.router)


@app.get("/")
def root():
    return {"status": "Axiom AI Backend Running"}