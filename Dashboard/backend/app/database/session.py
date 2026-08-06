import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _load_env() -> None:
    """Load env from Dashboard, shared AI-backend, or repo root."""
    here = Path(__file__).resolve()
    for candidate in (
        here.parents[1] / ".env",
        here.parents[2] / "AI-backend" / ".env",
        here.parents[2] / ".env",
    ):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


_load_env()

# Read SUPABASE_DB_URL matching your .env file
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

if not DATABASE_URL:
    raise ValueError("SUPABASE_DB_URL is missing or not loaded from .env")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()