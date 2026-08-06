"""Plain RAG service — Qdrant retrieval + Gemini synthesis (no CAG/CRAG)."""

from __future__ import annotations

import time
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable, RunnableParallel, RunnablePassthrough
from loguru import logger

from infrastructure.config import RETRIEVAL_SIMILARITY_THRESHOLD, RETRIEVAL_TOP_K
from infrastructure.db.qdrant_client import search_chunks
from infrastructure.utils import format_docs
from services.rag_service.rag_templates import RAG_TEMPLATE


class TenantQdrantRetriever(BaseRetriever):
    """LangChain retriever scoped to one tenant's Qdrant collection."""

    embedder: Any = None
    tenant_id: str = ""
    class_ids: list[str] | None = None
    top_k: int = RETRIEVAL_TOP_K
    score_threshold: float = RETRIEVAL_SIMILARITY_THRESHOLD

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> list[Document]:
        query_vec = self.embedder.embed_query(query)
        hits = search_chunks(
            tenant_id=self.tenant_id,
            query_vector=query_vec,
            top_k=self.top_k,
            score_threshold=self.score_threshold,
            class_ids=self.class_ids,
        )
        docs: list[Document] = []
        seen_parents: set[str] = set()
        for hit in hits:
            parent_id = hit.get("parent_id")
            if parent_id and parent_id in seen_parents:
                continue
            if parent_id:
                seen_parents.add(parent_id)
            page_content = hit.get("parent_text") or hit.get("chunk_text", "")
            docs.append(
                Document(
                    page_content=page_content,
                    metadata={
                        "url": hit.get("url", ""),
                        "title": hit.get("title", ""),
                        "lesson": hit.get("lesson", ""),
                        "score": hit.get("score", 0.0),
                        "tenant_id": self.tenant_id,
                        "child_text": hit.get("chunk_text", ""),
                        "parent_id": parent_id or "",
                    },
                )
            )
        return docs


def build_rag_chain(retriever: BaseRetriever, llm: Any, template: str = RAG_TEMPLATE) -> Runnable:
    rag_prompt = ChatPromptTemplate.from_template(template)
    return (
        RunnableParallel({"context": retriever | format_docs, "question": RunnablePassthrough()})
        | rag_prompt
        | llm
        | StrOutputParser()
    )


class RAGService:
    """Tenant-scoped RAG: retrieve tutor notes → synthesize grounded answer."""

    def __init__(
        self,
        *,
        tenant_id: str,
        embedder: Any,
        llm: Any,
        class_ids: list[str] | None = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.embedder = embedder
        self.llm = llm
        self.retriever = TenantQdrantRetriever(
            embedder=embedder,
            tenant_id=tenant_id,
            class_ids=class_ids,
            top_k=RETRIEVAL_TOP_K,
            score_threshold=RETRIEVAL_SIMILARITY_THRESHOLD,
        )
        self.chain = build_rag_chain(self.retriever, llm)

    def generate(self, query: str) -> dict[str, Any]:
        start = time.time()
        evidence = self.retriever.invoke(query)
        if not evidence:
            return {
                "answer": "",
                "evidence": [],
                "citations": [],
                "generation_time": time.time() - start,
                "num_docs": 0,
            }
        # Single retrieval pass — synthesize from evidence directly (chain would re-fetch).
        rag_prompt = ChatPromptTemplate.from_template(RAG_TEMPLATE)
        context = format_docs(evidence)
        response = self.llm.invoke(rag_prompt.format_messages(context=context, question=query))
        answer = response.content if hasattr(response, "content") else str(response)
        if isinstance(answer, list):
            answer = "\n".join(
                block.get("text", str(block)) if isinstance(block, dict) else str(block)
                for block in answer
            )
        answer = str(answer).strip()
        citations = []
        for doc in evidence:
            meta = doc.metadata or {}
            citations.append(
                {
                    "title": meta.get("title", ""),
                    "lesson": meta.get("lesson", ""),
                    "score": meta.get("score", 0.0),
                    "url": meta.get("url", ""),
                }
            )
        return {
            "answer": answer,
            "evidence": evidence,
            "citations": citations,
            "generation_time": time.time() - start,
            "num_docs": len(evidence),
        }
