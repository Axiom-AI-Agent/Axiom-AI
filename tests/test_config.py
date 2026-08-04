"""Config and tenant isolation unit tests."""

from infrastructure.config import (
    CHAT_MODEL,
    CHAT_PROVIDER,
    DEV_TENANT_ID,
    GUARDRAIL_MODEL,
    MERGE_MODEL,
    MERGE_PROVIDER,
    ROUTER_MODEL,
    qdrant_collection_for_tenant,
    validate,
)


def test_validate_creates_directories(tmp_path, monkeypatch):
    monkeypatch.setattr("infrastructure.config.DATA_DIR", tmp_path / "data")
    monkeypatch.setattr("infrastructure.config.KB_DIR", tmp_path / "kb")
    monkeypatch.setattr("infrastructure.config.LOGS_DIR", tmp_path / "logs")
    validate(require_llm=False, require_supabase=False)
    assert (tmp_path / "data").is_dir()


def test_qdrant_collection_per_tenant():
    assert qdrant_collection_for_tenant("tenant-a") != qdrant_collection_for_tenant("tenant-b")
    assert "tenant_a" in qdrant_collection_for_tenant("tenant-a")


def test_model_constants():
    assert ROUTER_MODEL
    assert GUARDRAIL_MODEL
    assert DEV_TENANT_ID.startswith("tenant-")


def test_chat_and_merge_model_split():
    assert CHAT_MODEL == "gpt-4o-mini"
    assert CHAT_PROVIDER == "openai"
    assert MERGE_MODEL == "gemini-2.5-flash"
    assert MERGE_PROVIDER == "google"
