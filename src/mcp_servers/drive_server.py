"""Drive MCP Server — papers, textbooks, syllabus only."""

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

from agents.tools.drive_tool import DriveTool

mcp = FastMCP("axiom-drive")
_tool: DriveTool | None = None


def _init() -> DriveTool:
    global _tool
    if _tool is None:
        logger.info("Initialising Drive MCP server...")
        _tool = DriveTool()
    return _tool


@mcp.tool()
def drive_search(tenant_id: str, query: str, folder: str | None = "papers") -> str:
    """Search tenant Drive for papers, textbooks, or syllabus files. Returns shareable links."""
    return _init().drive_search(tenant_id=tenant_id, query=query, folder=folder)


@mcp.tool()
def drive_list(tenant_id: str, folder: str = "papers") -> str:
    """List files in an allowed Drive subfolder (papers, textbooks, syllabus)."""
    return _init().drive_list(tenant_id=tenant_id, folder=folder)


if __name__ == "__main__":
    logger.info("Starting axiom-drive MCP server on stdio...")
    mcp.run()
