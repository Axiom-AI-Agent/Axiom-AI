"""Memory MCP server — exposes recall/add/procedural tools via stdio."""

from __future__ import annotations

from agents.tools.memory_tool import MemoryTool

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - optional at import time
    FastMCP = None  # type: ignore[misc, assignment]

mcp = FastMCP("axiom-memory") if FastMCP is not None else None
_tool = MemoryTool()


def _register_tools() -> None:
    if mcp is None:
        return

    @mcp.tool()
    def recall_turns(tenant_id: str, session_id: str, limit: int = 10) -> str:
        """Recall recent short-term turns for a session."""
        return _tool.recall_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            limit=limit,
        )

    @mcp.tool()
    def add_turn(
        tenant_id: str,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
    ) -> str:
        """Append a turn to short-term memory."""
        return _tool.add_turn(
            tenant_id=tenant_id,
            session_id=session_id,
            user_id=user_id,
            role=role,
            content=content,
        )

    @mcp.tool()
    def get_procedural(tenant_id: str, name: str | None = None) -> str:
        """Fetch procedural workflow definitions for a tenant."""
        return _tool.get_procedural(tenant_id=tenant_id, name=name)


_register_tools()


def main() -> None:
    if mcp is None:
        raise RuntimeError("fastmcp is required to run memory_server")
    mcp.run()


if __name__ == "__main__":
    main()
