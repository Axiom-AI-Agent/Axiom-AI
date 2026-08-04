"""RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from infrastructure.db.qdrant_client import collection_info, count_points
from infrastructure.llm import get_default_embeddings
from infrastructure.observability import observe
from services.rag_service.rag_service import RAGService


class RagTool:
    """Business logic for kb_search — used by rag_server and debug REST."""

    def __init__(self, *, embedder: Any | None = None, llm: Any | None = None) -> None:
        self._embedder = embedder
        self._llm = llm

    def _embedder_instance(self) -> Any:
        if self._embedder is None:
            self._embedder = get_default_embeddings()
        return self._embedder

    def _llm_instance(self) -> Any:
        if self._llm is None:
            # OpenAI chat model — faster + reliable for per-turn RAG synthesis.
            from infrastructure.llm import get_chat_llm

            self._llm = get_chat_llm(max_tokens=512)
        return self._llm

    @observe(name="kb_search")
    def kb_search(self, *, tenant_id: str, query: str) -> str:
        if not tenant_id:
            return json.dumps({"ok": False, "error": "tenant_id is required"})
        if not query or not query.strip():
            return json.dumps({"ok": False, "error": "query is required"})

        try:
            if count_points(tenant_id=tenant_id) == 0:
                return json.dumps(
                    {
                        "ok": True,
                        "answer": (
                            "I don't have tutor notes indexed for your class yet. "
                            "Please ask your tutor directly or try again later."
                        ),
                        "citations": [],
                        "num_docs": 0,
                    }
                )

            service = RAGService(
                tenant_id=tenant_id,
                embedder=self._embedder_instance(),
                llm=self._llm_instance(),
            )
            result = service.generate(query.strip())
            answer = result.get("answer", "").strip()
            if not answer:
                answer = (
                    "I couldn't find relevant tutor notes for that question. "
                    "Try rephrasing or ask your tutor in class."
                )
            return json.dumps(
                {
                    "ok": True,
                    "answer": answer,
                    "citations": result.get("citations") or [],
                    "num_docs": result.get("num_docs", 0),
                }
            )
        except Exception as exc:
            logger.exception("kb_search failed for tenant={}: {}", tenant_id, exc)
            return json.dumps({"ok": False, "error": str(exc)})

    def kb_ingest_status(self, *, tenant_id: str) -> str:
        if not tenant_id:
            return json.dumps({"ok": False, "error": "tenant_id is required"})
        try:
            points = count_points(tenant_id=tenant_id)
            info = collection_info(tenant_id=tenant_id) if points else {}
            return json.dumps(
                {
                    "ok": True,
                    "tenant_id": tenant_id,
                    "points_count": points,
                    "collection": info.get("collection"),
                    "ready": points > 0,
                }
            )
        except Exception as exc:
            logger.warning("kb_ingest_status failed: {}", exc)
            return json.dumps({"ok": True, "tenant_id": tenant_id, "points_count": 0, "ready": False})
