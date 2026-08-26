"""Cluster recent student questions into FAQ insights (no persistence)."""

from __future__ import annotations

import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from loguru import logger
from pydantic import BaseModel, Field

from infrastructure.db.supabase_client import get_supabase_client
from infrastructure.llm.llm_provider import get_chat_llm

_GREETING_NOISE = re.compile(
    r"^\s*("
    r"hi|hello|hey|yo|sup|thanks|thank you|ok|okay|yes|no|yep|nope|"
    r"good morning|good evening|good night|bye|see you"
    r")[\s!.?]*$",
    re.IGNORECASE,
)

_WHITESPACE = re.compile(r"\s+")


class FAQCluster(BaseModel):
    representative_question: str
    category: str = "general"
    source_indices: list[int] = Field(default_factory=list)
    example_questions: list[str] = Field(default_factory=list)
    suggested_answer: str = ""


class FAQClusterOutput(BaseModel):
    clusters: list[FAQCluster] = Field(default_factory=list)


def _clean_message(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = _WHITESPACE.sub(" ", str(text)).strip()
    if len(cleaned) < 8:
        return None
    if _GREETING_NOISE.match(cleaned):
        return None
    return cleaned


def load_recent_student_messages(
    *,
    tenant_id: str,
    limit: int = 200,
) -> list[str]:
    client = get_supabase_client()
    response = (
        client.table("st_turns")
        .select("content, role, created_at")
        .eq("tenant_id", tenant_id)
        .eq("role", "user")
        .order("created_at", desc=True)
        .limit(max(1, min(limit, 500)))
        .execute()
    )

    messages: list[str] = []
    for row in response.data or []:
        cleaned = _clean_message(row.get("content"))
        if cleaned:
            messages.append(cleaned)
    return messages


def analyze_faqs(
    *,
    tenant_id: str,
    limit: int = 200,
    minimum_frequency: int = 2,
) -> dict[str, Any]:
    messages = load_recent_student_messages(tenant_id=tenant_id, limit=limit)
    if not messages:
        return {
            "tenant_id": tenant_id,
            "analyzed_messages": 0,
            "clusters": [],
        }

    indexed = "\n".join(f"[{idx}] {text}" for idx, text in enumerate(messages))
    system = (
        "You analyze recurring student WhatsApp questions for a tuition centre. "
        "Group semantically equivalent questions. Return clusters with "
        "representative_question, category, source_indices (0-based indexes from "
        "the numbered list), up to 3 example_questions, and a short suggested_answer. "
        "Ignore one-off noise. Categories examples: fees, schedule, enrollment, "
        "materials, exams, general."
    )
    human = (
        f"Student messages (newest first):\n{indexed}\n\n"
        "Return JSON clusters only."
    )

    llm = get_chat_llm(max_tokens=2000)
    structured = llm.with_structured_output(FAQClusterOutput)

    try:
        result = structured.invoke(
            [
                SystemMessage(content=system),
                HumanMessage(content=human),
            ]
        )
    except Exception as exc:
        logger.error("FAQ analysis LLM failed: {}", exc)
        raise

    if isinstance(result, FAQClusterOutput):
        raw_clusters = result.clusters
    elif isinstance(result, dict):
        raw_clusters = FAQClusterOutput.model_validate(result).clusters
    else:
        raw_clusters = []

    clusters: list[dict[str, Any]] = []
    for cluster in raw_clusters:
        valid_indices = sorted(
            {
                index
                for index in cluster.source_indices
                if isinstance(index, int) and 0 <= index < len(messages)
            }
        )
        frequency = len(valid_indices)
        if frequency < max(1, minimum_frequency):
            continue

        examples = list(cluster.example_questions[:3])
        if not examples:
            examples = [messages[i] for i in valid_indices[:3]]

        clusters.append(
            {
                "question": cluster.representative_question.strip()
                or messages[valid_indices[0]],
                "category": (cluster.category or "general").strip().lower(),
                "frequency": frequency,
                "examples": examples,
                "suggested_answer": cluster.suggested_answer.strip(),
            }
        )

    clusters.sort(key=lambda item: item["frequency"], reverse=True)

    return {
        "tenant_id": tenant_id,
        "analyzed_messages": len(messages),
        "clusters": clusters,
    }
