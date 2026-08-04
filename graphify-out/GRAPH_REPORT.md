# Graph Report - Axiom-AI  (2026-08-04)

## Corpus Check
- 107 files · ~374,110 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 894 nodes · 1578 edges · 85 communities (72 shown, 13 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 286 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `954b2dab`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Roadmap.md
- Infrastructure Support
- 23. Important Classes
- Tasks
- Tasks
- 3. Folder-by-Folder Explanation
- Tasks
- Appendix: Complete File Inventory
- Phase 1 — Twilio WhatsApp Sandbox Pipeline
- Week 13 Technical Documentation
- 8. LLM Integration
- 29. How I Can Build a Similar Project
- Agent Core
- 5. Architecture
- 8\. Functional Requirements
- 14. Configuration
- config.py
- Tutor_AI_SRS_v2.md
- health.py
- test_health.py
- supabase_client.py
- 7. Agentic AI Design
- Chat Flow
- Retrieval and Ingestion
- 13. APIs
- 16. Execution Flow
- 2. Overall Project Structure
- 30. Learning Notes
- 4\. Stakeholders and User Roles
- 11. Retrieval
- 22. Key Algorithms
- 9\. Non-Functional Requirements
- 21. Dependency Graph
- 24. Important Functions
- 9. Memory
- 25. Data Models
- 12. Database
- 28. How Everything Connects
- 10\. System Architecture Overview (High Level)
- 16\. Constraints and Assumptions
- 2\. Purpose, Scope, and Definitions
- 18. Security
- 3\. Market and Competitive Context
- 7\. User Stories
- init_supabase.py
- run.py
- llm/__init__.py
- src/__init__.py
- axiom-ai-backend
- agents/__init__.py
- Memory Core
- README.md
- middleware.py
- 2. LLM Model Strategy
- 3. Status Enums & Domain Types
- 4. Langfuse Observability & Prompt Management
- 5. System Understanding
- 7. Multi-Tenant Data Model
- 6. Resource Split: Google Drive vs RAG
- 9. High-Level Architecture
- tutoring_prompts.py
- verify_phase0.py
- Setup & Migration
- Memory Tables
- seed_langfuse_prompts.py
- deps.py
- nodes/__init__.py
- agents/prompts/__init__.py
- admissions/__init__.py
- identity/__init__.py
- messaging/__init__.py
- conftest.py

## God Nodes (most connected - your core abstractions)
1. `AgentState` - 33 edges
2. `AgentOrchestrator` - 26 edges
3. `OnboardingFlow` - 26 edges
4. `IdentityContext` - 24 edges
5. `ChatPipeline` - 24 edges
6. `QueryRouter` - 23 edges
7. `get_supabase_client()` - 23 edges
8. `CrmTool` - 20 edges
9. `MemoryTool` - 19 edges
10. `Axiom AI — AI Backend Roadmap` - 19 edges

## Surprising Connections (you probably didn't know these)
- `test_trace_context_tags_and_metadata()` --calls--> `TraceContext`  [INFERRED]
  tests/test_observability.py → src/infrastructure/observability.py
- `main()` --calls--> `get_supabase_client()`  [INFERRED]
  scripts/clear_demo_session.py → src/infrastructure/db/supabase_client.py
- `main()` --calls--> `get_langfuse_client()`  [INFERRED]
  scripts/seed_langfuse_prompts.py → src/infrastructure/observability.py
- `main()` --calls--> `reset_langfuse_state()`  [INFERRED]
  scripts/seed_langfuse_prompts.py → src/infrastructure/observability.py
- `main()` --calls--> `run_chat_turn()`  [INFERRED]
  scripts/smoke_langfuse_trace.py → src/agents/chat_pipeline.py

## Import Cycles
- None detected.

## Communities (85 total, 13 thin omitted)

### Community 0 - "Roadmap.md"
Cohesion: 0.22
Nodes (9): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 0 — Foundation & Multi-Tenant Schema, Reference Implementation (copy — do not invent) (+1 more)

### Community 1 - "Infrastructure Support"
Cohesion: 0.05
Nodes (35): Protocol, main(), AdmissionsAgent, AdmissionsAgentResult, CrmClient, DirectCrmClient, _last_user_text(), McpCrmClient (+27 more)

### Community 2 - "23. Important Classes"
Cohesion: 0.06
Nodes (52): AnyMessage, GuardrailVerdict, main(), _primary_route(), RoutingCase, _run(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A (+44 more)

### Community 3 - "Tasks"
Cohesion: 0.22
Nodes (9): 11. API Contract Summary (Dashboard Team), 12. Environment Variables, 13. Explicitly Out of MVP Scope, 14. Per-Phase Workflow, 15. Day-by-Day Schedule, 1. Locked Architecture Decisions, Appendix: Generic Template, Axiom AI — AI Backend Roadmap (+1 more)

### Community 4 - "Tasks"
Cohesion: 0.06
Nodes (40): main(), main(), main(), main(), post, Send a student message and receive an AI reply.      Use this during development, send_chat_message(), ChatChannel (+32 more)

### Community 5 - "3. Folder-by-Folder Explanation"
Cohesion: 0.12
Nodes (18): patch, parse_twilio_form(), Parse Twilio application/x-www-form-urlencoded webhook bodies., chat_result(), client(), fixture, HTTP dev chat endpoint tests., test_chat_returns_reply() (+10 more)

### Community 6 - "Tasks"
Cohesion: 0.22
Nodes (12): get_current_trace_id(), langfuse_turn_attributes(), Any, Propagate tenant/session/user identifiers to all nested Langfuse observations., OpenTelemetry / Langfuse trace id for the active context, if any., Propagate user/session/tags to nested spans for one chat turn., Langfuse trace scope for a WhatsApp conversation turn., trace_context() (+4 more)

### Community 7 - "Appendix: Complete File Inventory"
Cohesion: 0.14
Nodes (17): BackgroundTasks, _parse_form_params(), post, Request, Response, Twilio WhatsApp webhook router., Twilio WhatsApp sandbox webhook.      Returns 200 immediately and processes the, _should_validate_signature() (+9 more)

### Community 8 - "Phase 1 — Twilio WhatsApp Sandbox Pipeline"
Cohesion: 0.07
Nodes (42): BaseChatModel, ChatOpenAI, main(), build_agent_mcp(), build_orchestrator(), In-process MemoryTool path (dev/tests without MCP subprocesses)., MCP path — memory tools via stdio server (Week 13 pattern)., get_api_key() (+34 more)

### Community 9 - "Week 13 Technical Documentation"
Cohesion: 0.21
Nodes (15): BaseException, _disable_langfuse(), get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), prefetch_prompts(), Langfuse observability — tracing per tenant/session/user and prompt hooks.  Prom (+7 more)

### Community 10 - "8. LLM Integration"
Cohesion: 0.15
Nodes (13): Application Access Patterns, Axiom AI — Database Documentation, Demo Seed Data, ENUM Types, ER Diagram, ER entity → SQL table mapping, Legacy v1 Tables (removed), Multi-Tenancy (+5 more)

### Community 11 - "29. How I Can Build a Similar Project"
Cohesion: 0.17
Nodes (12): `audit_logs` (AUDIT_LOG), `bank_slip_uploads` (BANK_SLIP_UPLOAD), `enrollments` (ENROLLMENT), `escalations` (ESCALATION), `invoices` (INVOICE), `message_logs` (MESSAGE_LOG), `parent_guardians` (PARENT_GUARDIAN), `staff_users` (STAFF_USER) (+4 more)

### Community 12 - "Agent Core"
Cohesion: 0.22
Nodes (7): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 13 - "5. Architecture"
Cohesion: 0.17
Nodes (12): Architecture, Dev Chat — WhatsApp Simulator (No Twilio Required), Endpoints, Fetch conversation history, Prerequisites, Reference implementations, Related docs, Request body (+4 more)

### Community 14 - "8\. Functional Requirements"
Cohesion: 0.33
Nodes (6): 8.1 Agentic Workforce and Conversational Interface, 8.2 Financial and Ticket Management, 8.3 Administrative Dashboard and Agency CRM, 8.5 Marketing and Lead Management, 8.6 Platform Administration and Multi-Tenancy (New), 8\. Functional Requirements

### Community 15 - "14. Configuration"
Cohesion: 0.27
Nodes (11): build_direct_system_prompt(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_router_prompt(), get_admissions_stub_reply(), get_escalation_stub_reply(), get_payment_stub_reply(), get_resource_stub_reply() (+3 more)

### Community 16 - "config.py"
Cohesion: 0.06
Nodes (26): Memory business logic — called by MCP server only (Week 13 pattern)., list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant., get_supabase_client(), list_tenants() (+18 more)

### Community 17 - "Tutor_AI_SRS_v2.md"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 18 - "health.py"
Cohesion: 0.10
Nodes (43): Enum, get_chat_turns(), get, HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required)., Fetch recent conversation turns for a student session., active_config(), health(), get (+35 more)

### Community 19 - "test_health.py"
Cohesion: 0.21
Nodes (9): FastAPI, LogRecord, lifespan(), get, FastAPI application — Phase 3 admissions agent + dev chat + Twilio webhook., root(), _InterceptHandler, Centralised loguru setup (stderr-only for future MCP safety). (+1 more)

### Community 20 - "supabase_client.py"
Cohesion: 0.17
Nodes (12): 16.10 V2 Architecture Upgrades (Reference Patterns), 16.11 V2 Acceptance Themes, 16.1 Messaging & Infrastructure, 16.2 AI Agents & Orchestration, 16.3 Memory, Caching & RAG Enhancements, 16.4 Payments & Finance Automation, 16.5 Integrations & Tooling, 16.6 CRM, Dashboard & Backend APIs (Extended) (+4 more)

### Community 21 - "7. Agentic AI Design"
Cohesion: 0.27
Nodes (11): create_enrollment(), get_student(), _init(), list_classes(), tool, CRM MCP Server — admissions actions (register_student, get_student, list_classes, Update student profile during onboarding (name, school, district, consent)., Fetch student profile and active enrollments by phone. (+3 more)

### Community 22 - "Chat Flow"
Cohesion: 0.25
Nodes (8): main(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., reset_agent_runtime(), flush(), Process inbound student messages and produce agent replies.

### Community 23 - "Retrieval and Ingestion"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 24 - "13. APIs"
Cohesion: 0.24
Nodes (5): FakeCrmClient, asyncio, Admissions agent node tests (in-process CRM, no MCP subprocess)., test_admissions_agent_asks_consent_before_enrollment(), test_admissions_agent_prompts_for_name_on_first_turn()

### Community 25 - "16. Execution Flow"
Cohesion: 0.31
Nodes (9): add_turn(), get_procedural(), _init(), tool, Memory MCP Server — exposes ST recall / add_turn / procedural lookup.  Adapted f, Fetch recent conversation turns for a tenant session., Append a conversation turn to short-term memory., Lookup tenant onboarding / workflow procedures. (+1 more)

### Community 26 - "2. Overall Project Structure"
Cohesion: 0.22
Nodes (9): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 1 — Dev Chat + Messaging Pipeline *(Twilio deferred)*, Reference Implementation (copy — do not invent) (+1 more)

### Community 27 - "30. Learning Notes"
Cohesion: 0.28
Nodes (8): get_student(), Any, get, post, Student registration and lookup — dashboard + dev API., Register or update a student profile (dashboard / manual onboarding)., Fetch student profile and enrollments by phone., register_student()

### Community 28 - "4\. Stakeholders and User Roles"
Cohesion: 0.50
Nodes (4): 4.1 User Role Overview, 4.2 Student Profile, 4.3 Tutor and Agency Admin Profile, 4\. Stakeholders and User Roles

### Community 29 - "11. Retrieval"
Cohesion: 0.25
Nodes (3): client(), fixture, Phase 0 health endpoint tests.

### Community 30 - "22. Key Algorithms"
Cohesion: 0.29
Nodes (5): BaseHTTPMiddleware, Request, Response, Request ID and latency headers., RequestContextMiddleware

### Community 31 - "9\. Non-Functional Requirements"
Cohesion: 0.25
Nodes (8): 9.1 Usability and Accessibility, 9.2 Performance and Scalability, 9.3 Reliability and Availability, 9.4 Security, 9.5 Data Privacy and Regulatory Compliance, 9.6 Messaging and AI Cost Governance (New), 9.7 Maintainability and Observability, 9\. Non-Functional Requirements

### Community 32 - "21. Dependency Graph"
Cohesion: 0.29
Nodes (7): 8.1 MCP Tool Architecture (MVP), 8. Reference Patterns to Reuse, Debug / REST parity, `mcp_config.py`, MCP servers (MVP scope), Tenant context, Wiring pattern

### Community 33 - "24. Important Functions"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Dependencies, Features, Files / Modules, Objective, Phase 2 — Agent Framework (Decision Graph + Chat Pipeline), Reference Implementation (copy — do not invent)

### Community 34 - "9. Memory"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Features, Files / Modules, Google Drive MVP Approach, Objective, Phase 4 — Resource Agent (Drive + RAG), Reference Implementation (copy — do not invent)

### Community 35 - "25. Data Models"
Cohesion: 0.33
Nodes (6): Test helper — clear cached Langfuse client state., reset_langfuse_state(), Observability helper tests., setup_function(), teardown_function(), test_trace_context_tags_and_metadata()

### Community 36 - "12. Database"
Cohesion: 0.33
Nodes (6): 10. Phased Implementation Plan, Acceptance Criteria, Features, Objective, Phase 6 — Integration, Testing & Handoff, Reference Implementation (copy — do not invent)

### Community 37 - "28. How Everything Connects"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features, Files / Modules, Objective, Phase 3 — Admissions Agent, Reference Implementation (copy — do not invent)

### Community 38 - "10\. System Architecture Overview (High Level)"
Cohesion: 0.67
Nodes (3): 10.1 Agent Roster, 10.2 Conceptual Data Flow, 10\. System Architecture Overview (High Level)

### Community 39 - "16\. Constraints and Assumptions"
Cohesion: 0.67
Nodes (3): 16.1 Constraints, 16.2 Assumptions, 16\. Constraints and Assumptions

### Community 40 - "2\. Purpose, Scope, and Definitions"
Cohesion: 0.67
Nodes (3): 2.1 Purpose, 2.2 In Scope / Out of Scope, 2\. Purpose, Scope, and Definitions

### Community 41 - "18. Security"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features, Files / Modules, Objective, Phase 5 — Payment Check, Escalation & Dashboard APIs, Reference Implementation (copy — do not invent)

### Community 42 - "3\. Market and Competitive Context"
Cohesion: 0.67
Nodes (3): 3.1 Adjacent Tools and Why They Fall Short, 3.2 Tutor AI's Differentiation, 3\. Market and Competitive Context

### Community 43 - "7\. User Stories"
Cohesion: 0.67
Nodes (3): 7.1 Student and Parent Stories, 7.2 Tutor and Admin Stories (CRM Focused), 7\. User Stories

### Community 49 - "agents/__init__.py"
Cohesion: 0.08
Nodes (35): F, ChatResult, _format_memory_context(), _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, _routes_from_patch() (+27 more)

### Community 56 - "Memory Core"
Cohesion: 0.60
Nodes (5): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory()

### Community 59 - "middleware.py"
Cohesion: 0.29
Nodes (4): db_conn(), _db_url(), fixture, Validate v2 ER schema tables exist in Supabase when DATABASE_URL is configured.

### Community 60 - "2. LLM Model Strategy"
Cohesion: 0.40
Nodes (5): 2. LLM Model Strategy, Config Files, Merge Points (Gemini), Model Assignments (Locked for MVP), Why Two Models?

### Community 61 - "3. Status Enums & Domain Types"
Cohesion: 0.40
Nodes (5): 3. Status Enums & Domain Types, Enum ↔ Langfuse Tags, PostgreSQL ENUM Types (`sql/01_schema.sql`), Python Enums (`src/domain/enums.py`), Rules

### Community 62 - "4. Langfuse Observability & Prompt Management"
Cohesion: 0.40
Nodes (5): 4. Langfuse Observability & Prompt Management, Environment, Phase Deliverables for Langfuse, Prompt Management — Langfuse as Source of Truth, Tracing — Per Tenant, Session, User

### Community 63 - "5. System Understanding"
Cohesion: 0.40
Nodes (5): 5. System Understanding, Agent Roster (MVP — 4 specialists + router), Business Problem, MVP Solution (AI Backend), Success Metrics (from MVP Definition)

### Community 64 - "7. Multi-Tenant Data Model"
Cohesion: 0.50
Nodes (4): 7. Multi-Tenant Data Model, Core Entities, Shared Supabase for Dashboard Team, Tenant Resolution (Inbound Twilio)

### Community 65 - "6. Resource Split: Google Drive vs RAG"
Cohesion: 0.67
Nodes (3): 6. Resource Split: Google Drive vs RAG, Google Drive — Tutes & Textbooks Only, RAG (Qdrant) — Tutor Notes Only

### Community 66 - "9. High-Level Architecture"
Cohesion: 0.67
Nodes (3): 9. High-Level Architecture, Decision Graph — BookMe-AI Pattern (No CAG/CRAG), Processing Model (No Redis)

### Community 69 - "verify_phase0.py"
Cohesion: 0.83
Nodes (3): check_live(), main(), run_pytest()

### Community 70 - "Setup & Migration"
Cohesion: 0.40
Nodes (5): Apply schema, Manual apply (Supabase SQL editor), Prerequisites, Setup & Migration, Verify

### Community 71 - "Memory Tables"
Cohesion: 0.40
Nodes (5): `mem_episodes`, `mem_facts`, `mem_procedures`, Memory Tables, `st_turns`

### Community 72 - "seed_langfuse_prompts.py"
Cohesion: 0.60
Nodes (4): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog()

### Community 73 - "deps.py"
Cohesion: 0.60
Nodes (4): get_request_id(), Request, FastAPI dependency injection helpers., _require_startup()

## Knowledge Gaps
- **170 isolated node(s):** `axiom-ai-backend`, `RoutingCase`, `Quick start (Phase 0)`, `Overview`, `Technology` (+165 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `McpCrmClient` connect `Infrastructure Support` to `Phase 1 — Twilio WhatsApp Sandbox Pipeline`, `agents/__init__.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `CrmTool` connect `Infrastructure Support` to `config.py`, `30. Learning Notes`, `7. Agentic AI Design`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `AgentState` connect `agents/__init__.py` to `Infrastructure Support`, `23. Important Classes`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `AgentState` (e.g. with `AdmissionsAgent` and `AdmissionsAgentResult`) actually correct?**
  _`AgentState` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `AgentOrchestrator` (e.g. with `ChatResult` and `McpCrmClient`) actually correct?**
  _`AgentOrchestrator` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `OnboardingFlow` (e.g. with `main()` and `AdmissionsAgent`) actually correct?**
  _`OnboardingFlow` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `IdentityContext` (e.g. with `main()` and `main()`) actually correct?**
  _`IdentityContext` has 9 INFERRED edges - model-reasoned connections that need verification._