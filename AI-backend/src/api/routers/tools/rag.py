"""Debug REST — RAG tool (same surface as rag_server MCP)."""

from __future__ import annotations

import asyncio
import time

from fastapi import APIRouter, Depends, Query

from agents.tools.rag_tool import RagTool
from api.deps import get_rag_tool
from api.schemas import RAGResponse, RAGSearchRequest, RAGStatusResponse

router = APIRouter(prefix="/tools/rag", tags=["Tools — RAG"])


@router.post("/search", response_model=RAGResponse)
async def search(req: RAGSearchRequest, rag: RagTool = Depends(get_rag_tool)) -> RAGResponse:
    t0 = time.perf_counter()
    raw = await asyncio.to_thread(rag.kb_search, tenant_id=req.tenant_id, query=req.query)
    return RAGResponse(result=raw, latency_ms=int((time.perf_counter() - t0) * 1000))


@router.get("/status", response_model=RAGStatusResponse)
async def status(
    tenant_id: str = Query(...),
    rag: RagTool = Depends(get_rag_tool),
) -> RAGStatusResponse:
    raw = await asyncio.to_thread(rag.kb_ingest_status, tenant_id=tenant_id)
    return RAGStatusResponse(result=raw)
