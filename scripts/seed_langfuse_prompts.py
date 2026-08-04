#!/usr/bin/env python3
"""Upload local prompt fallbacks to Langfuse (production label)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env", override=True)

from agents.prompts import agent_prompts as ap
from infrastructure.config import LANGFUSE_PROMPT_LABEL
from infrastructure.observability import get_langfuse_client, reset_langfuse_state

_VAR_RE = re.compile(r"(?<!\{)\{([a-z_]+)\}(?!\})")


def _langfuse_template(text: str) -> str:
    """Convert Python .format `{var}` placeholders to Langfuse `{{var}}`."""
    return _VAR_RE.sub(r"{{\1}}", text)


def _seed_catalog() -> list[tuple[str, str, str]]:
    return [
        (ap.LANGFUSE_PROMPT_NAMES["guardrail_system"], "text", _langfuse_template(ap._GUARDRAIL_SYSTEM_FALLBACK)),
        (ap.LANGFUSE_PROMPT_NAMES["router_system"], "text", _langfuse_template(ap._ROUTER_SYSTEM_FALLBACK)),
        (ap.LANGFUSE_PROMPT_NAMES["router_hard_rules"], "text", ap._ROUTER_HARD_RULES_FALLBACK),
        (ap.LANGFUSE_PROMPT_NAMES["router_user"], "text", _langfuse_template(ap._ROUTER_USER_FALLBACK)),
        (ap.LANGFUSE_PROMPT_NAMES["direct_system"], "text", _langfuse_template(ap._DIRECT_SYSTEM_FALLBACK)),
        (ap.LANGFUSE_PROMPT_NAMES["merge_system"], "text", _langfuse_template(ap._MERGE_SYSTEM_FALLBACK)),
        (ap.LANGFUSE_PROMPT_NAMES["out_of_scope_reply"], "text", ap._OUT_OF_SCOPE_REPLY_FALLBACK.strip()),
        (ap.LANGFUSE_PROMPT_NAMES["admissions_stub"], "text", ap._ADMISSIONS_STUB_FALLBACK.strip()),
        (ap.LANGFUSE_PROMPT_NAMES["resource_stub"], "text", ap._RESOURCE_STUB_FALLBACK.strip()),
        (ap.LANGFUSE_PROMPT_NAMES["payment_stub"], "text", ap._PAYMENT_STUB_FALLBACK.strip()),
        (ap.LANGFUSE_PROMPT_NAMES["escalation_stub"], "text", ap._ESCALATION_STUB_FALLBACK.strip()),
    ]


def main() -> int:
    reset_langfuse_state()
    client = get_langfuse_client()
    if client is None:
        print("FAIL: Langfuse unavailable — check LANGFUSE_* keys and LANGFUSE_HOST")
        return 1

    label = LANGFUSE_PROMPT_LABEL
    print(f"=== Seeding Langfuse prompts (label={label}) ===")
    seeded = 0
    for name, prompt_type, prompt in _seed_catalog():
        client.create_prompt(
            name=name,
            type=prompt_type,
            prompt=prompt,
            labels=[label],
        )
        print(f"  + {name} ({prompt_type})")
        seeded += 1

    print(f"Done: {seeded} prompts uploaded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
