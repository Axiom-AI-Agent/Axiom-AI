from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import classes, payments, students, escalations
from app.database.session import engine, Base

import app.models  # noqa: F401 — register all ORM models with metadata

# Create tables in Supabase automatically on boot
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Axiom AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classes.router)
app.include_router(payments.router)
app.include_router(students.router)
app.include_router(escalations.router)


@app.get("/")
def root():
    return {"status": "Axiom AI Backend Running"}