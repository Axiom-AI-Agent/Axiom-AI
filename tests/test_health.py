"""Phase 0 health endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["service"] == "Axiom AI"
    assert body["phase"] == 5


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["phase"] == 4


def test_config(client):
    response = client.get("/config")
    assert response.status_code == 200
    body = response.json()
    assert body["chat_model"] == "gpt-4o-mini"
    assert body["chat_provider"] == "openai"
    assert body["merge_model"] == "gemini-2.0-flash"
    assert body["merge_provider"] == "google"
    assert "router_model" in body
    assert "guardrail_model" in body
    assert "langfuse_prompt_label" in body


def test_request_id_header(client):
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers
