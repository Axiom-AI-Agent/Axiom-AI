"""Pytest bootstrap — load project .env before tests (matches api.main and scripts)."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)
