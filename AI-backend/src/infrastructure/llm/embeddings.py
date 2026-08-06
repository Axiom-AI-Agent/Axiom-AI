"""OpenAI embeddings for RAG ingest and retrieval."""

from __future__ import annotations

from typing import Any

from langchain_openai import OpenAIEmbeddings

from infrastructure.config import EMBEDDING_MODEL, EMBEDDING_PROVIDER, OPENROUTER_BASE_URL, get_api_key


def get_default_embeddings(
    batch_size: int = 100,
    show_progress: bool = False,
    **kwargs: Any,
) -> OpenAIEmbeddings:
    """Return configured embedding model (text-embedding-3-small by default)."""
    llm_kwargs: dict[str, Any] = dict(
        model=EMBEDDING_MODEL,
        show_progress_bar=show_progress,
        **kwargs,
    )
    if EMBEDDING_PROVIDER == "openrouter":
        llm_kwargs["openai_api_base"] = OPENROUTER_BASE_URL
        llm_kwargs["openai_api_key"] = get_api_key("openrouter")
    else:
        llm_kwargs["openai_api_key"] = get_api_key(EMBEDDING_PROVIDER)
    return OpenAIEmbeddings(**llm_kwargs)
