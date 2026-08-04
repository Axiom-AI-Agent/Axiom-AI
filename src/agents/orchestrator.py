"""
Axiom AI orchestrator — LangGraph fan-out after the decision subgraph.

Ported from BookMe AI ``agents/orchestrator.py``; travel agents replaced with
tuition specialists (direct live; others stubbed for Phases 3–5).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agents.prompts import (
    build_direct_system_prompt,
    build_merge_system_prompt,
    get_escalation_stub_reply,
    get_payment_stub_reply,
    get_resource_stub_reply,
)
from agents.nodes.admissions_agent import McpCrmClient, run_admissions_agent
from agents.router import QueryRouter, get_query_router
from agents.state import AgentState
from agents.tools.memory_tool import MemoryTool
from infrastructure.llm import get_chat_llm, get_merge_llm
from infrastructure.observability import observe

EmitFn = Callable[[dict[str, Any]], Awaitable[None]]

_ROUTE_TO_NODE = {
    "admissions": "admissions",
    "resource": "resource",
    "payment_check": "payment_check",
    "escalation": "escalation",
    "direct": "direct",
}


@dataclass
class AgentResponse:
    answer: str
    route: str = "direct"
    routes: list[str] = field(default_factory=list)
    action: str | None = None
    tool_output: str = ""
    memory_context: str = ""
    latency_ms: int = 0


def _emit_from_config(config: RunnableConfig | None) -> EmitFn | None:
    if config and (cfg := config.get("configurable")):
        fn = cfg.get("emit")
        if fn is not None:
            return fn
    return None


def _last_user_text(state: AgentState) -> str:
    messages = state.get("messages") or []
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = msg.content
            return content if isinstance(content, str) else str(content)
        if isinstance(msg, dict) and msg.get("role") == "user":
            return str(msg.get("content") or "")
    return ""


def _llm_content_to_str(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("text"):
                parts.append(str(block["text"]))
        return "\n".join(parts)
    return str(content)


async def _invoke_llm_text(llm: Any, messages: list) -> str:
    response = await llm.ainvoke(messages)
    return _llm_content_to_str(response.content if hasattr(response, "content") else response)


def _format_session_memory(memory_tool: MemoryTool, state: AgentState) -> str:
    tenant_id = state.get("tenant_id") or ""
    user_id = state.get("user_id") or ""
    session_id = state.get("session_id") or ""
    if not tenant_id or not session_id:
        return ""
    try:
        return memory_tool.recall_turns(
            tenant_id=tenant_id,
            session_id=session_id,
            user_id=user_id,
            limit=10,
        )
    except Exception as exc:
        logger.warning("Session recall failed: {}", exc)
        return ""


def _mcp_result_to_str(raw: Any) -> str:
    if isinstance(raw, list):
        parts = [
            item.get("text", str(item)) for item in raw if isinstance(item, dict)
        ]
        return "\n".join(parts) if parts else str(raw)
    return str(raw)


class _MCPMemoryToolAdapter:
    """MCP memory tools → async dispatch (Week 13 / BookMe MCP adapter pattern)."""

    _ACTION_TO_TOOL = {
        "recall": "recall_turns",
        "add": "add_turn",
        "procedural": "get_procedural",
    }

    def __init__(self, tools_by_name: dict):
        self._tools = tools_by_name

    async def recall_turns(
        self,
        *,
        tenant_id: str,
        session_id: str,
        user_id: str,
        limit: int = 10,
    ) -> str:
        tool = self._tools.get("recall_turns")
        if tool is None:
            return "(memory MCP unavailable)"
        raw = await tool.ainvoke(
            {
                "tenant_id": tenant_id,
                "session_id": session_id,
                "user_id": user_id,
                "limit": limit,
            }
        )
        return _mcp_result_to_str(raw)


class AgentOrchestrator:
    def __init__(
        self,
        llm_chat: Any,
        *,
        llm_merge: Any | None = None,
        memory_tool: MemoryTool | None = None,
        mcp_memory: _MCPMemoryToolAdapter | None = None,
        mcp_crm: McpCrmClient | None = None,
        router: QueryRouter | None = None,
    ) -> None:
        self.llm_chat = llm_chat
        self.llm_merge = llm_merge or llm_chat
        self.memory_tool = memory_tool or MemoryTool()
        self.mcp_memory = mcp_memory
        self.mcp_crm = mcp_crm
        self.router = router or get_query_router()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("recall", self.recall_node)
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("direct_agent", self.direct_agent_node)
        workflow.add_node("admissions_agent", self.admissions_agent_node)
        workflow.add_node("resource_agent", self.resource_agent_node)
        workflow.add_node("payment_check_agent", self.payment_check_agent_node)
        workflow.add_node("escalation_agent", self.escalation_agent_node)
        workflow.add_node("merge_responses", self.merge_responses_node)

        workflow.add_conditional_edges(
            START,
            self.entry_routing,
            {"end": END, "recall": "recall"},
        )
        workflow.add_edge("recall", "supervisor")
        workflow.add_conditional_edges(
            "supervisor",
            self.supervisor_routing,
            {
                "direct": "direct_agent",
                "admissions": "admissions_agent",
                "resource": "resource_agent",
                "payment_check": "payment_check_agent",
                "escalation": "escalation_agent",
            },
        )
        for node in (
            "direct_agent",
            "admissions_agent",
            "resource_agent",
            "payment_check_agent",
            "escalation_agent",
        ):
            workflow.add_edge(node, "merge_responses")
        workflow.add_edge("merge_responses", END)
        return workflow.compile()

    def entry_routing(self, state: AgentState) -> str:
        if state.get("verdict") == "out_of_scope":
            return "end"
        return "recall"

    @observe(name="node_recall")
    async def recall_node(self, state: AgentState) -> dict[str, Any]:
        if state.get("memory_context"):
            return {}
        tenant_id = state.get("tenant_id") or ""
        user_id = state.get("user_id") or ""
        session_id = state.get("session_id") or ""

        if self.mcp_memory and tenant_id and session_id:
            memory_context = await self.mcp_memory.recall_turns(
                tenant_id=tenant_id,
                session_id=session_id,
                user_id=user_id,
            )
        else:
            patch = dict(state)
            memory_context = _format_session_memory(self.memory_tool, patch)  # type: ignore[arg-type]

        return {"memory_context": memory_context or "(no prior turns)"}

    @observe(name="node_supervisor")
    async def supervisor_node(self, state: AgentState) -> dict[str, Any]:
        if state.get("route_decisions"):
            return {}
        user_message = _last_user_text(state)
        memory_context = state.get("memory_context") or ""
        multi = await self.router.aroute(user_message, memory_context)
        return {"route_decisions": [asdict(d) for d in multi.decisions]}

    def supervisor_routing(self, state: AgentState) -> str | list[str]:
        decisions = state.get("route_decisions") or []
        if not decisions:
            return "direct"
        node_names: list[str] = []
        seen: set[str] = set()
        for d in decisions:
            route = d.get("route", "direct")
            node = _ROUTE_TO_NODE.get(route, "direct")
            if node not in seen:
                node_names.append(node)
                seen.add(node)
        if len(node_names) == 1:
            return node_names[0]
        return node_names

    async def _generate_direct_response(
        self,
        state: AgentState,
        config: RunnableConfig | None = None,
    ) -> str:
        user_message = _last_user_text(state)
        memory_context = state.get("memory_context") or ""
        tenant_name = state.get("tenant_name") or "your tuition centre"
        system_prompt = build_direct_system_prompt(
            memory_context=memory_context,
            tenant_name=tenant_name,
        )
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ]
        _ = _emit_from_config(config)
        return await _invoke_llm_text(self.llm_chat, messages)

    @observe(name="node_direct_agent")
    async def direct_agent_node(
        self,
        state: AgentState,
        config: RunnableConfig | None = None,
    ) -> dict[str, Any]:
        answer = await self._generate_direct_response(state, config)
        return {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [{"route": "direct", "tool_output": "", "answer": answer, "status": "ok"}],
        }

    @observe(name="node_admissions_agent")
    async def admissions_agent_node(self, state: AgentState) -> dict[str, Any]:
        return await run_admissions_agent(state, crm=self.mcp_crm)

    @observe(name="node_resource_agent")
    async def resource_agent_node(self, state: AgentState) -> dict[str, Any]:
        answer = get_resource_stub_reply()
        return {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [{"route": "resource", "tool_output": "", "answer": answer, "status": "ok"}],
        }

    @observe(name="node_payment_check_agent")
    async def payment_check_agent_node(self, state: AgentState) -> dict[str, Any]:
        answer = get_payment_stub_reply()
        return {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [{"route": "payment_check", "tool_output": "", "answer": answer, "status": "ok"}],
        }

    @observe(name="node_escalation_agent")
    async def escalation_agent_node(self, state: AgentState) -> dict[str, Any]:
        answer = get_escalation_stub_reply()
        return {
            "messages": [AIMessage(content=answer)],
            "agent_outputs": [{"route": "escalation", "tool_output": "", "answer": answer, "status": "ok"}],
        }

    @observe(name="node_merge_responses")
    async def merge_responses_node(
        self,
        state: AgentState,
        config: RunnableConfig | None = None,
    ) -> dict[str, Any]:
        agent_outputs = state.get("agent_outputs") or []
        if len(agent_outputs) <= 1:
            if agent_outputs:
                out = agent_outputs[0]
                return {
                    "final_answer": out.get("answer", ""),
                    "tool_output": out.get("tool_output", ""),
                }
            return {}

        user_message = _last_user_text(state)
        memory_context = state.get("memory_context") or ""
        combined = ""
        for out in agent_outputs:
            route = out.get("route", "unknown").upper()
            combined += f"=== {route} AGENT ===\n{out.get('answer', '')}\n\n"

        system_prompt = build_merge_system_prompt(memory_context=memory_context)
        messages = [
            SystemMessage(content=f"{system_prompt}\n\n=== FRAGMENTS ===\n{combined}"),
            HumanMessage(content=user_message),
        ]
        try:
            merged = await _invoke_llm_text(self.llm_merge, messages)
        except Exception as exc:
            logger.warning("Merge LLM failed ({}); using first fragment.", exc)
            merged = agent_outputs[0].get("answer", "")
        return {
            "final_answer": merged,
            "messages": [AIMessage(content=merged)],
            "tool_output": combined,
        }

    async def arun_state(
        self,
        state: AgentState,
        *,
        config: RunnableConfig | None = None,
    ) -> AgentState:
        merged = dict(state)
        merged["agent_outputs"] = []
        return await self.graph.ainvoke(merged, config=config or {})  # type: ignore[return-value]

    def _to_agent_response(self, final_state: dict, latency_ms: int) -> AgentResponse:
        route_decisions = final_state.get("route_decisions") or []
        all_routes = [d.get("route", "direct") for d in route_decisions]
        primary = route_decisions[0] if route_decisions else {"route": "direct"}
        if not all_routes and final_state.get("verdict") == "out_of_scope":
            all_routes = ["out_of_scope"]
        return AgentResponse(
            answer=final_state.get("final_answer") or "",
            route=primary.get("route", "direct"),
            routes=all_routes or ["direct"],
            action=primary.get("action"),
            tool_output=final_state.get("tool_output", ""),
            memory_context=final_state.get("memory_context", ""),
            latency_ms=latency_ms,
        )


def build_orchestrator(*, memory_tool: MemoryTool | None = None) -> AgentOrchestrator:
    """In-process MemoryTool path (dev/tests without MCP subprocesses)."""
    return AgentOrchestrator(
        get_chat_llm(),
        llm_merge=get_merge_llm(),
        memory_tool=memory_tool or MemoryTool(),
    )


async def build_agent_mcp(*, memory_tool: MemoryTool | None = None) -> AgentOrchestrator:
    """MCP path — memory tools via stdio server (Week 13 pattern)."""
    from langchain_mcp_adapters.client import MultiServerMCPClient

    from mcp_servers.mcp_config import build_mcp_server_config

    server_config = build_mcp_server_config()
    logger.info("Connecting to MCP servers: {}", list(server_config.keys()))
    mcp_client = MultiServerMCPClient(server_config)
    all_tools = await mcp_client.get_tools()
    tools_by_name = {t.name: t for t in all_tools}
    logger.info("Loaded {} MCP tools: {}", len(all_tools), list(tools_by_name.keys()))

    orchestrator = AgentOrchestrator(
        get_chat_llm(),
        llm_merge=get_merge_llm(),
        memory_tool=memory_tool or MemoryTool(),
        mcp_memory=_MCPMemoryToolAdapter(tools_by_name),
        mcp_crm=McpCrmClient(tools_by_name),
    )
    orchestrator.mcp_client = mcp_client
    orchestrator.mcp_tools = tools_by_name
    return orchestrator
