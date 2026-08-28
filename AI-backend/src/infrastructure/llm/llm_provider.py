"""LLM factories — guardrail/router/chat/extractor (GPT-4o-mini), merge (Gemini). Groq provider retained for optional use."""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from infrastructure.config import (
    CHAT_MODEL,
    CHAT_PROVIDER,
    EXTRACTOR_MODEL,
    EXTRACTOR_PROVIDER,
    GROQ_BASE_URL,
    GUARDRAIL_MODEL,
    GUARDRAIL_PROVIDER,
    MERGE_MODEL,
    MERGE_PROVIDER,
    OPENROUTER_BASE_URL,
    ROUTER_MODEL,
    ROUTER_PROVIDER,
    get_api_key,
)


def _build_openai_compatible_llm(
    model: str,
    provider: str,
    *,
    temperature: float = 0,
    streaming: bool = False,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> ChatOpenAI:
    llm_kwargs: dict[str, Any] = dict(
        model=model,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens,
        **kwargs,
    )
    if provider == "openrouter":
        llm_kwargs["openai_api_base"] = OPENROUTER_BASE_URL
        llm_kwargs["openai_api_key"] = get_api_key("openrouter")
    elif provider == "groq":
        llm_kwargs["openai_api_base"] = GROQ_BASE_URL
        llm_kwargs["openai_api_key"] = get_api_key("groq")
    elif provider == "openai":
        llm_kwargs["openai_api_key"] = get_api_key("openai")
    return ChatOpenAI(**llm_kwargs)


def _build_google_llm(
    model: str,
    *,
    temperature: float = 0,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    api_key = get_api_key("google")
    if not api_key:
        return _build_openai_compatible_llm(
            f"google/{model}",
            "openrouter",
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        max_output_tokens=max_tokens,
        google_api_key=api_key,
        timeout=30,
        **kwargs,
    )


def _build_llm(
    model: str,
    provider: str,
    *,
    temperature: float = 0,
    streaming: bool = False,
    max_tokens: int | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    if provider in ("google", "gemini"):
        return _build_google_llm(
            model, temperature=temperature, max_tokens=max_tokens, **kwargs
        )
    return _build_openai_compatible_llm(
        model,
        provider,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens,
        **kwargs,
    )


def get_router_llm(**kwargs: Any) -> BaseChatModel:
    return _build_llm(ROUTER_MODEL, ROUTER_PROVIDER, temperature=0, **kwargs)


def get_guardrail_llm(**kwargs: Any) -> BaseChatModel:
    return _build_llm(GUARDRAIL_MODEL, GUARDRAIL_PROVIDER, temperature=0, **kwargs)


def get_extractor_llm(**kwargs: Any) -> BaseChatModel:
    return _build_llm(EXTRACTOR_MODEL, EXTRACTOR_PROVIDER, temperature=0, **kwargs)


def get_fast_chat_llm(**kwargs: Any) -> BaseChatModel:
    return _build_llm(EXTRACTOR_MODEL, EXTRACTOR_PROVIDER, temperature=0.3, **kwargs)


def get_chat_llm(**kwargs: Any) -> BaseChatModel:
    """Primary specialist agent model — OpenAI GPT-4o-mini."""
    return _build_llm(CHAT_MODEL, CHAT_PROVIDER, temperature=0, **kwargs)


def get_merge_llm(**kwargs: Any) -> BaseChatModel:
    """Merge / synthesis model — Google Gemini."""
    return _build_llm(MERGE_MODEL, MERGE_PROVIDER, temperature=0.2, **kwargs)


def get_fallback_llm(**kwargs: Any) -> BaseChatModel:
    """Ultra-fast fallback model for degraded mode handling."""
    return _build_llm("llama-3.1-8b-instant", "groq", temperature=0, **kwargs)
