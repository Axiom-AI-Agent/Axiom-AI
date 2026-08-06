from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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