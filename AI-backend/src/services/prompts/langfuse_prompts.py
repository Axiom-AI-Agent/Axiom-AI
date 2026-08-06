"""Langfuse prompt management with local fallback seeds."""

from __future__ import annotations

from typing import Any

from loguru import logger

from agents.prompts.tutoring_prompts import LOCAL_PROMPTS
from infrastructure.config import LANGFUSE_PROMPT_LABEL
from infrastructure.observability import (
    _disable_langfuse,
    _is_langfuse_auth_error,
    get_langfuse_client,
)


class PromptService:
    """Fetch and compile prompts from Langfuse; fall back to local seeds."""

    def __init__(self, *, label: str | None = None) -> None:
        self.label = label or LANGFUSE_PROMPT_LABEL

    def get_text(self, name: str, **variables: Any) -> str:
        compiled = self._fetch(name, **variables)
        if isinstance(compiled, str):
            return compiled
        raise TypeError(f"Prompt {name!r} is not a text prompt")

    def get_messages(self, name: str, **variables: Any) -> list[dict[str, str]]:
        compiled = self._fetch(name, **variables)
        if isinstance(compiled, list):
            return compiled
        if isinstance(compiled, str):
            return [{"role": "user", "content": compiled}]
        raise TypeError(f"Prompt {name!r} could not be compiled to messages")

    def _fetch(self, name: str, **variables: Any) -> str | list[dict[str, str]]:
        client = get_langfuse_client()
        if client is not None:
            try:
                prompt = client.get_prompt(name, label=self.label)
                return prompt.compile(**variables)
            except Exception as exc:
                if _is_langfuse_auth_error(exc):
                    _disable_langfuse("prompt fetch unauthorized")
                else:
                    logger.debug("Langfuse prompt {} unavailable: {}", name, exc)

        return self._local_fallback(name, **variables)

    def _local_fallback(self, name: str, **variables: Any) -> str | list[dict[str, str]]:
        logger.debug("Using local prompt fallback for {}", name)
        template = LOCAL_PROMPTS.get(name)
        if template is None:
            raise KeyError(f"No Langfuse or local prompt registered for {name!r}")

        if isinstance(template, str):
            return self._substitute_variables(template, **variables)

        messages: list[dict[str, str]] = []
        for message in template:
            content = self._substitute_variables(message["content"], **variables)
            messages.append({"role": message["role"], "content": content})
        return messages

    @staticmethod
    def _substitute_variables(template: str, **variables: Any) -> str:
        """Support Langfuse `{{var}}` and local `{var}` placeholders."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
            result = result.replace(f"{{{key}}}", str(value))
        return result


prompt_service = PromptService()
