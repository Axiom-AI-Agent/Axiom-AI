"""
Application configuration — YAML + environment variables.

Secrets live only in `.env`. Tunable parameters in `config/*.yaml`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"


def _load_yaml(filename: str) -> dict[str, Any]:
    path = _CONFIG_DIR / filename
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _get_nested(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return default if current is None else current


def _get_str(d: dict[str, Any], *keys: str, default: str) -> str:
    value = _get_nested(d, *keys, default=default)
    return value if isinstance(value, str) else default


_PARAMS = _load_yaml("param.yaml")
_MODELS = _load_yaml("models.yaml")

PROJECT_ROOT = _PROJECT_ROOT
PROVIDER = _get_str(_PARAMS, "provider", "default", default="openai")
MODEL_TIER = _get_str(_PARAMS, "provider", "tier", default="general")
OPENROUTER_BASE_URL = _get_str(
    _PARAMS, "provider", "openrouter_base_url", default="https://openrouter.ai/api/v1"
)
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

EMBEDDING_TIER = _get_str(_PARAMS, "embedding", "tier", default="small")
EMBEDDING_PROVIDER = _get_str(_PARAMS, "embedding", "provider", default="openai")

LANGFUSE_HOST = os.getenv("LANGFUSE_HOST") or os.getenv(
    "LANGFUSE_BASE_URL", "https://cloud.langfuse.com"
)
LANGFUSE_PROMPT_LABEL = os.getenv("LANGFUSE_PROMPT_LABEL", "production")


def _env_bool(name: str, *, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# Set LANGFUSE_ENABLED=false in .env to skip tracing/prompt fetch (local fallbacks only).
LANGFUSE_ENABLED = _env_bool("LANGFUSE_ENABLED", default=True)


def get_chat_model(provider: str | None = None, tier: str | None = None) -> str:
    provider_key = provider or PROVIDER
    tier_key = tier or MODEL_TIER
    if provider_key == "gemini":
        provider_key = "google"
    return _get_str(_MODELS, provider_key, "chat", tier_key, default="gpt-4o-mini")


def get_role_config(role: str) -> tuple[str, str]:
    """Return (model, provider) for an LLM role defined in param.yaml."""
    provider = _get_str(_PARAMS, "llm", "roles", role, "provider", default=PROVIDER)
    tier = _get_str(_PARAMS, "llm", "roles", role, "tier", default=MODEL_TIER)
    if provider == "gemini":
        provider = "google"
    model = get_chat_model(provider, tier)
    return model, provider


ROUTER_MODEL, ROUTER_PROVIDER = get_role_config("router")
GUARDRAIL_MODEL, GUARDRAIL_PROVIDER = get_role_config("guardrail")
EXTRACTOR_MODEL, EXTRACTOR_PROVIDER = get_role_config("extractor")
CHAT_MODEL, CHAT_PROVIDER = get_role_config("chat")
MERGE_MODEL, MERGE_PROVIDER = get_role_config("merge")
FAST_CHAT_MODEL = EXTRACTOR_MODEL
FAST_CHAT_PROVIDER = EXTRACTOR_PROVIDER


def get_embedding_model(provider: str | None = None, tier: str | None = None) -> str:
    provider_key = provider or PROVIDER
    tier_key = tier or EMBEDDING_TIER
    if provider_key in ("google", "gemini"):
        provider_key = "google"
    return _get_str(
        _MODELS, provider_key, "embedding", tier_key, default="text-embedding-3-small"
    )


EMBEDDING_MODEL = get_embedding_model(provider=EMBEDDING_PROVIDER)
EMBEDDING_DIM = 1536 if EMBEDDING_TIER == "small" else 3072

LLM_TEMPERATURE = float(_get_nested(_PARAMS, "llm", "temperature", default=0.0))
LLM_MAX_TOKENS = int(_get_nested(_PARAMS, "llm", "max_tokens", default=2000))

RETRIEVAL_TOP_K = int(_get_nested(_PARAMS, "retrieval", "top_k", default=4))
RETRIEVAL_SIMILARITY_THRESHOLD = float(
    _get_nested(_PARAMS, "retrieval", "similarity_threshold", default=0.35)
)
RETRIEVAL_ESCALATION_THRESHOLD = float(
    _get_nested(
        _PARAMS,
        "retrieval",
        "escalation_threshold",
        default=0.45,
    )
)

FIXED_CHUNK_SIZE = int(_get_nested(_PARAMS, "chunking", "fixed", "chunk_size", default=800))
FIXED_CHUNK_OVERLAP = int(_get_nested(_PARAMS, "chunking", "fixed", "chunk_overlap", default=100))
PARENT_CHUNK_SIZE = int(_get_nested(_PARAMS, "chunking", "parent_child", "parent_size", default=1200))
CHILD_CHUNK_SIZE = int(_get_nested(_PARAMS, "chunking", "parent_child", "child_size", default=250))
CHILD_CHUNK_OVERLAP = int(_get_nested(_PARAMS, "chunking", "parent_child", "child_overlap", default=50))
EMBEDDING_BATCH_SIZE = int(_get_nested(_PARAMS, "embedding", "batch_size", default=100))

GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
DRIVE_MOCK = os.getenv("DRIVE_MOCK", "false").lower() in ("1", "true", "yes", "on")
# When false, resource tools require MCP clients (no DirectDriveClient/DirectRagClient fallback).
ALLOW_INPROCESS_TOOLS = _env_bool("ALLOW_INPROCESS_TOOLS", default=True)
DRIVE_ALLOWED_FOLDERS = frozenset({"papers", "textbooks", "syllabus"})

DATA_DIR = PROJECT_ROOT / _get_str(_PARAMS, "paths", "data_dir", default="data")
KB_DIR = PROJECT_ROOT / _get_str(_PARAMS, "paths", "kb_dir", default="data/knowledge_base")
UPLOADS_DIR = PROJECT_ROOT / _get_str(_PARAMS, "paths", "uploads_dir", default="data/uploads")
LOGS_DIR = PROJECT_ROOT / _get_str(_PARAMS, "paths", "logs_dir", default="logs")

LOG_LEVEL = _get_str(_PARAMS, "logging", "level", default="INFO")
OBSERVABILITY_ENABLED = bool(_get_nested(_PARAMS, "observability", "enabled", default=True))

ST_MAX_TURNS = int(_get_nested(_PARAMS, "memory", "st_max_turns", default=30))
ST_TTL_SECONDS = int(_get_nested(_PARAMS, "memory", "st_ttl_seconds", default=86400))

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_PREFIX = _get_str(_PARAMS, "qdrant", "collection_prefix", default="axiom_kb")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_VALIDATE_SIGNATURE = os.getenv("TWILIO_VALIDATE_SIGNATURE", "true").lower() == "true"
MESSAGING_DRY_RUN = os.getenv("MESSAGING_DRY_RUN", "true").lower() == "true"

DEV_TENANT_ID = os.getenv("DEV_TENANT_ID", "tenant-demo-physics")
TIMEZONE = "Asia/Colombo"


def get_api_key(provider: str | None = None) -> str | None:
    provider_name = provider or PROVIDER
    key_map = {
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY",
    }
    env_var = key_map.get(provider_name, f"{provider_name.upper()}_API_KEY")
    return os.getenv(env_var)


def langfuse_configured() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))


def validate(*, require_supabase: bool = False, require_llm: bool = True) -> None:
    """Validate config and ensure data directories exist."""
    if require_llm:
        has_chat = bool(get_api_key(CHAT_PROVIDER))
        has_merge = bool(get_api_key(MERGE_PROVIDER))
        has_router = bool(get_api_key(ROUTER_PROVIDER))
        if not (has_chat or has_merge or has_router):
            raise ValueError(
                "Missing LLM API key: set OPENAI_API_KEY, GOOGLE_API_KEY, "
                "GROQ_API_KEY, and/or OPENROUTER_API_KEY in .env"
            )

    if require_supabase:
        if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")

    for directory in (DATA_DIR, KB_DIR, UPLOADS_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def qdrant_collection_for_tenant(tenant_id: str) -> str:
    safe = tenant_id.replace("-", "_")
    return f"{QDRANT_COLLECTION_PREFIX}_{safe}"
