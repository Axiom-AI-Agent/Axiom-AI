#!/usr/bin/env python3
"""Smoke-test LLM factory wiring."""

from __future__ import annotations

import sys

from dotenv import load_dotenv

load_dotenv(override=True)

from infrastructure.config import get_api_key, validate
from infrastructure.llm.llm_provider import get_chat_llm, get_merge_llm, get_router_llm


def main() -> None:
    validate(require_llm=False, require_supabase=False)
    if not any(get_api_key(p) for p in ("groq", "openai", "google", "openrouter")):
        print("Skip: no LLM keys configured (set keys in .env to smoke-test factories)")
        sys.exit(0)

    router = get_router_llm()
    chat = get_chat_llm()
    merge = get_merge_llm()
    print(f"Router LLM: {router.model_name}")
    print(f"Chat LLM:   {chat.model_name}")
    print(f"Merge LLM:  {merge.model_name}")
    print("OK")


if __name__ == "__main__":
    main()
