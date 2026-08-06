"""RAG MCP Server — tenant-scoped tutor-note Q&A."""

from __future__ import annotations

import os
import sys

_SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from dotenv import load_dotenv

load_dotenv()

from loguru import logger
from mcp.server.fastmcp import FastMCP

from agents.tools.rag_tool import RagTool

mcp = FastMCP("axiom-rag")
_tool: RagTool | None = None


def _init() -> RagTool:
    global _tool
    if _tool is None:
        logger.info("Initialising RAG MCP server...")
        _tool = RagTool()
    return _tool


@mcp.tool()
def kb_search(tenant_id: str, query: str, class_ids: list[str] | None = None) -> str:
    """Search tutor lesson notes (Qdrant) and return a grounded answer with citations."""
    return _init().kb_search(tenant_id=tenant_id, query=query, class_ids=class_ids)


@mcp.tool()
def kb_ingest_status(tenant_id: str) -> str:
    """Return Qdrant ingest status for a tenant's tutor-note collection."""
    return _init().kb_ingest_status(tenant_id=tenant_id)


if __name__ == "__main__":
    logger.info("Starting axiom-rag MCP server on stdio...")
    mcp.run()
