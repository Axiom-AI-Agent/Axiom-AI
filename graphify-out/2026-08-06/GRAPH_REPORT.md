# Graph Report - Axiom-AI  (2026-08-06)

## Corpus Check
- 272 files · ~424,521 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2348 nodes · 4085 edges · 216 communities (191 shown, 25 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 712 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fe731163`
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
- Axiom AI Backend — Finalize Checklist
- IdentityContext
- compilerOptions
- get_supabase_client
- FastAPI
- resource_agent.py
- api/schemas.py
- compilerOptions
- IdentityResolver
- FastAPI Best Practices
- Upstash Patterns
- Google Drive MCP — Integration & Testing
- CrmTool
- Database Patterns
- Dashboard API Contract (Phase 5)
- models/__init__.py
- run_chat_turn
- DriveTool
- MockDriveBackend
- ResourceAgent
- RagTool
- rag_service.py
- ChatChannel
- Demo UI Plan — WhatsApp Mock + Full Agent Lifecycle
- models/enums.py
- routes/escalations.py
- get_conversation_thread
- Phase 6 — Implementation Plan
- MessagePersistence
- dashboard/escalations.py
- map_decision_to_agent_state
- MessageLog
- test_tenant_scope.py
- Axiom AI — Setup Guide (Phase 6)
- QueryRouter
- escalation_reasons.py
- Quick Patterns
- memory.py
- EscalationAgent
- router.py
- test_e2e_smoke.py
- Sidebar.tsx
- overview/page.tsx
- api.ts
- .create_escalation
- routes/students.py
- compilerOptions
- Phase 5 — Design Decisions (As Implemented)
- tenant_scope.py
- SubjectClass
- ShortTermMemoryStore
- test_dashboard_api.py
- turn_to_record
- main
- AGENTS.md — Axiom AI Backend
- health.py
- build_mcp_server_config
- Security Patterns
- Demo UI — WhatsApp Student Chat
- dashboard_overview
- PaymentStatusUpdate
- drive_server.py
- rag_server.py
- test_ingest_upload.py
- app/layout.tsx
- Phase 5 — Escalations + staff chat
- TwilioMessagingClient
- get_chat_logs
- Demo script — Student chat only (~5 min)
- list_classes
- DriveResponse
- upload_document
- supabase_client.py
- test_router_intents.py
- send_chat_message
- 8. Implementation phases
- test_merge_response.py
- Axiom AI - Dashboard Backend
- vite.config.ts
- test_run_resource_agent_requires_mcp_clients_when_fallback_disabled
- classes.ts
- vite-env.d.ts
- main
- Dashboard/AGENTS.md
- eslint.config.mjs
- next.config.ts
- postcss.config.mjs
- dashboard/__init__.py
- routers/escalations.py
- .list_recent_sessions
- rag_templates.py
- config.py
- PaymentAgent
- Path
- fixed_chunk
- debug_drive_integration.py
- .drive_list
- IdentityResolver
- test_chat.py
- AdmissionsAgentResult
- onboarding_route.py
- ingest_documents
- smoke_drive_paper_link
- ._assert_tenant
- MockDriveBackend
- approve_payment
- log.py
- get_default_embeddings
- smoke_mcp_memory.py
- .resolve_escalation
- document_from_pdf
- test_config.py
- smoke_resource.py
- get_summary
- preload_agent_runtime
- main
- admissions_db_client.py

## God Nodes (most connected - your core abstractions)
1. `OnboardingFlow` - 54 edges
2. `AgentState` - 53 edges
3. `get_supabase_client()` - 52 edges
4. `IdentityContext` - 45 edges
5. `CrmTool` - 38 edges
6. `MessageRole` - 32 edges
7. `DriveTool` - 32 edges
8. `AgentOrchestrator` - 30 edges
9. `RagTool` - 30 edges
10. `AdmissionsDbClient` - 30 edges

## Surprising Connections (you probably didn't know these)
- `test_router_parses_json_routes()` --calls--> `QueryRouter`  [INFERRED]
  tests/test_decision_graph.py → src/agents/router.py
- `test_create_payment_escalation()` --calls--> `CrmTool`  [INFERRED]
  tests/test_payment_escalation.py → src/agents/tools/crm_tool.py
- `test_create_talk_to_tutor_escalation()` --calls--> `CrmTool`  [INFERRED]
  tests/test_payment_escalation.py → src/agents/tools/crm_tool.py
- `test_reject_payment_escalation()` --calls--> `CrmTool`  [INFERRED]
  tests/test_payment_escalation.py → src/agents/tools/crm_tool.py
- `test_resolve_payment_escalation_activates_enrollment()` --calls--> `CrmTool`  [INFERRED]
  tests/test_payment_escalation.py → src/agents/tools/crm_tool.py

## Import Cycles
- None detected.

## Communities (216 total, 25 thin omitted)

### Community 0 - "Roadmap.md"
Cohesion: 0.22
Nodes (9): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 0 — Foundation & Multi-Tenant Schema, Reference Implementation (copy — do not invent) (+1 more)

### Community 1 - "Infrastructure Support"
Cohesion: 0.06
Nodes (30): Pattern, OnboardingFlow, OnboardingSlots, OnboardingState, Any, Multi-turn admissions onboarding — slot tracking and class disambiguation., Determine onboarding progress and extract slots from user messages., Hydrate state for an existing database student (post-enrollment paths only). (+22 more)

### Community 2 - "23. Important Classes"
Cohesion: 0.14
Nodes (15): decide_node(), _emit_from_config(), make_router_node(), Any, EmitFn, RunnableConfig, Decision LangGraph — guardrail and router subgraph for Axiom AI.  Ported from Bo, Agent framework — decision graph + orchestrator (Phase 2). (+7 more)

### Community 3 - "Tasks"
Cohesion: 0.22
Nodes (9): 11. API Contract Summary (Dashboard Team), 12. Environment Variables, 13. Explicitly Out of MVP Scope, 14. Per-Phase Workflow, 15. Day-by-Day Schedule, 1. Locked Architecture Decisions, Appendix: Generic Template, Axiom AI — AI Backend Roadmap (+1 more)

### Community 4 - "Tasks"
Cohesion: 0.13
Nodes (16): main(), main(), ChatPipeline, Channel-agnostic chat pipeline — HTTP dev chat + Twilio webhook., Sync entry for scripts and tests without a running event loop., ChatTurnResult, InboundMessage, BaseModel (+8 more)

### Community 5 - "3. Folder-by-Folder Explanation"
Cohesion: 0.18
Nodes (7): parse_twilio_form(), Parse Twilio application/x-www-form-urlencoded webhook bodies., client(), identity_ctx(), fixture, Twilio webhook endpoint tests., test_parse_twilio_form_extracts_media()

### Community 6 - "Tasks"
Cohesion: 0.17
Nodes (15): get_current_trace_id(), langfuse_turn_attributes(), Any, Langfuse observability — tracing per tenant/session/user and prompt hooks.  Prom, Propagate tenant/session/user identifiers to all nested Langfuse observations., OpenTelemetry / Langfuse trace id for the active context, if any., Propagate user/session/tags to nested spans for one chat turn., Langfuse trace scope for a WhatsApp conversation turn. (+7 more)

### Community 7 - "Appendix: Complete File Inventory"
Cohesion: 0.14
Nodes (17): BackgroundTasks, _parse_form_params(), post, Request, Response, Twilio WhatsApp webhook router., Twilio WhatsApp sandbox webhook.      Returns 200 immediately and processes the, _should_validate_signature() (+9 more)

### Community 8 - "Phase 1 — Twilio WhatsApp Sandbox Pipeline"
Cohesion: 0.23
Nodes (19): BaseChatModel, ChatOpenAI, main(), get_api_key(), Validate config and ensure data directories exist., validate(), _build_google_llm(), _build_llm() (+11 more)

### Community 9 - "Week 13 Technical Documentation"
Cohesion: 0.19
Nodes (15): BaseException, _disable_langfuse(), get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), prefetch_prompts(), Validate API keys once at startup; avoids repeated 401 noise from prompt fetch. (+7 more)

### Community 10 - "8. LLM Integration"
Cohesion: 0.06
Nodes (35): Application Access Patterns, Apply schema, `audit_logs` (AUDIT_LOG), Axiom AI — Database Documentation, `bank_slip_uploads` (BANK_SLIP_UPLOAD), Demo Seed Data, `enrollments` (ENROLLMENT), ENUM Types (+27 more)

### Community 11 - "29. How I Can Build a Similar Project"
Cohesion: 0.06
Nodes (45): QUICK_ACTIONS, detectLifecycleProgress(), emptyLifecycle(), includesAny(), LIFECYCLE_STEPS, LifecycleState, LifecycleStep, LifecycleStepId (+37 more)

### Community 12 - "Agent Core"
Cohesion: 0.20
Nodes (8): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Support Langfuse `{{var}}` and local `{var}` placeholders., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 13 - "5. Architecture"
Cohesion: 0.17
Nodes (12): Architecture, Dev Chat — WhatsApp Simulator (No Twilio Required), Endpoints, Fetch conversation history, Prerequisites, Reference implementations, Related docs, Request body (+4 more)

### Community 14 - "8\. Functional Requirements"
Cohesion: 0.33
Nodes (6): 8.1 Agentic Workforce and Conversational Interface, 8.2 Financial and Ticket Management, 8.3 Administrative Dashboard and Agency CRM, 8.5 Marketing and Lead Management, 8.6 Platform Administration and Multi-Tenancy (New), 8\. Functional Requirements

### Community 15 - "14. Configuration"
Cohesion: 0.20
Nodes (17): build_direct_system_prompt(), build_escalation_ack_reply(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply(), build_resource_drive_reply(), build_resource_rag_reply() (+9 more)

### Community 16 - "config.py"
Cohesion: 0.19
Nodes (6): Memory business logic — called by MCP server only (Week 13 pattern)., ProceduralMemoryStore, Procedural memory store — tenant-scoped ``mem_procedures`` lookup.  Adapted from, Procedure, Memory schemas — ported from Week 13 ``memory/schemas.py`` (MVP subset)., Short-term memory store — Supabase ``st_turns`` ring buffer.  Adapted from Week

### Community 17 - "Tutor_AI_SRS_v2.md"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 18 - "health.py"
Cohesion: 0.18
Nodes (16): ChatChannel, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, MessageRole, PaymentStatus, Enum (+8 more)

### Community 19 - "test_health.py"
Cohesion: 0.18
Nodes (8): BaseHTTPMiddleware, get, FastAPI application — Phase 6 integration (MCP warmup + dashboard APIs)., root(), Request, Response, Request ID and latency headers., RequestContextMiddleware

### Community 20 - "supabase_client.py"
Cohesion: 0.17
Nodes (12): 16.10 V2 Architecture Upgrades (Reference Patterns), 16.11 V2 Acceptance Themes, 16.1 Messaging & Infrastructure, 16.2 AI Agents & Orchestration, 16.3 Memory, Caching & RAG Enhancements, 16.4 Payments & Finance Automation, 16.5 Integrations & Tooling, 16.6 CRM, Dashboard & Backend APIs (Extended) (+4 more)

### Community 21 - "7. Agentic AI Design"
Cohesion: 0.12
Nodes (29): commit_onboarding(), create_enrollment(), create_escalation(), get_class_details(), get_student(), get_tenant_info(), _init(), list_classes() (+21 more)

### Community 22 - "Chat Flow"
Cohesion: 0.20
Nodes (16): main(), scenario_out_of_scope(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., Close MCP subprocess client on app shutdown (Week 13 / BookMe pattern)., reset_agent_runtime() (+8 more)

### Community 23 - "Retrieval and Ingestion"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 24 - "13. APIs"
Cohesion: 0.21
Nodes (17): AdmissionsAgent, get_onboarding_session_store(), clear_onboarding_sessions(), FakeCrmClient, asyncio, fixture, Admissions agent node tests (in-process CRM, no MCP subprocess)., _state() (+9 more)

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
Cohesion: 0.22
Nodes (15): Distance, Document, QdrantClient, qdrant_collection_for_tenant(), collection_exists(), collection_info(), count_points(), delete_collection() (+7 more)

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
Cohesion: 0.28
Nodes (8): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog(), Test helper — clear cached Langfuse client state., reset_langfuse_state(), setup_function(), teardown_function()

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
Nodes (6): Acceptance Criteria, Features *(original plan — see PHASE5_DECISIONS.md for what changed)*, Files / Modules, Objective, Phase 5 — Payment Check, Escalation & Dashboard APIs, Reference Implementation (copy — do not invent)

### Community 42 - "3\. Market and Competitive Context"
Cohesion: 0.67
Nodes (3): 3.1 Adjacent Tools and Why They Fall Short, 3.2 Tutor AI's Differentiation, 3\. Market and Competitive Context

### Community 43 - "7\. User Stories"
Cohesion: 0.67
Nodes (3): 7.1 Student and Parent Stories, 7.2 Tutor and Admin Stories (CRM Focused), 7\. User Stories

### Community 49 - "agents/__init__.py"
Cohesion: 0.21
Nodes (12): F, run_admissions_agent(), AgentOrchestrator, _emit_from_config(), _last_user_text(), Any, EmitFn, RunnableConfig (+4 more)

### Community 56 - "Memory Core"
Cohesion: 0.14
Nodes (16): DirectDriveClient, McpDriveClient, McpRagClient, AgentResponse, build_agent_mcp(), build_orchestrator(), _format_session_memory(), _invoke_llm_text() (+8 more)

### Community 57 - "README.md"
Cohesion: 0.67
Nodes (3): Axiom AI — Backend, Docs, Quick start

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
Cohesion: 0.10
Nodes (8): CrmClient, DirectCrmClient, McpCrmClient, Any, Protocol, Shared CRM client protocol for agent nodes (direct + MCP paths)., MCP CRM tools → async dispatch., In-process CRM path (dev/tests without MCP subprocesses).

### Community 71 - "Memory Tables"
Cohesion: 0.04
Nodes (44): autoprefixer, clsx, dependencies, clsx, framer-motion, lucide-react, react, react-dom (+36 more)

### Community 72 - "seed_langfuse_prompts.py"
Cohesion: 0.05
Nodes (40): chart.js, dependencies, chart.js, framer-motion, lucide-react, next, react, react-chartjs-2 (+32 more)

### Community 73 - "deps.py"
Cohesion: 0.15
Nodes (13): get_drive_tool(), get_rag_tool(), get_request_id(), Request, FastAPI dependency injection helpers., _require_startup(), list_files(), post (+5 more)

### Community 81 - "conftest.py"
Cohesion: 0.38
Nodes (6): active_tenant_scope(), client(), client_no_tenant_override(), fixture, Pytest bootstrap — load project .env before tests (matches api.main and scripts), HTTP client without tenant dependency override (for auth rejection tests).

### Community 85 - "Axiom AI Backend — Finalize Checklist"
Cohesion: 0.06
Nodes (33): Agent pipeline, Axiom AI Backend — Finalize Checklist, Bot & environment, Core agent & routing, Dashboard handoff, Demo UI (`demo-ui-org/`), Documentation, Documentation sync (+25 more)

### Community 86 - "IdentityContext"
Cohesion: 0.16
Nodes (17): ResourceAgent, build_recall_context(), format_student_profile(), Build recall context (student profile + ST turns) before the decision graph., Structured student block for router and agent prompts., Return (full_router_context, student_profile_context) for one chat turn., FakeDrive, FakeMemoryTool (+9 more)

### Community 87 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 88 - "get_supabase_client"
Cohesion: 0.19
Nodes (5): get_supabase_client(), Return a singleton Supabase client (requires service role key)., AdmissionsDbClient, Any, Tenant-scoped student, class, and enrollment persistence.

### Community 89 - "FastAPI"
Cohesion: 0.15
Nodes (13): get_db(), get, root(), InvoiceStatus, Invoice, Base, Represents a student's invoice for a specific billing period., create_invoice() (+5 more)

### Community 90 - "resource_agent.py"
Cohesion: 0.11
Nodes (18): ResourceSubPath, classify_resource_subpath(), DirectRagClient, DriveClient, _infer_drive_folder(), _last_user_text(), _mcp_text(), Any (+10 more)

### Community 91 - "api/schemas.py"
Cohesion: 0.25
Nodes (29): MessageRole, PaymentStatus, TenantStatus, post, search(), ChatConversationsResponse, ChatConversationSummary, ChatRequest (+21 more)

### Community 92 - "compilerOptions"
Cohesion: 0.08
Nodes (26): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+18 more)

### Community 93 - "IdentityResolver"
Cohesion: 0.16
Nodes (15): main(), main(), _one_turn(), main(), get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session. (+7 more)

### Community 94 - "FastAPI Best Practices"
Cohesion: 0.08
Nodes (25): API Design, Async Routes, Async Test Client from Day 0, Chain Dependencies, CPU Intensive Tasks, Custom Base Model, Decouple BaseSettings, Dependencies (+17 more)

### Community 95 - "Upstash Patterns"
Cohesion: 0.08
Nodes (23): Basic Setup, Batch Messages, Best Practices, FastAPI Caching, FastAPI Rate Limiting, FastAPI Session Management, Hash Operations, Key Expiration (TTL) (+15 more)

### Community 96 - "Google Drive MCP — Integration & Testing"
Cohesion: 0.08
Nodes (24): 1. Google Cloud, 2. Environment, Architecture, Folder ID, Folder layout, Google Drive MCP — Integration & Testing, Multi-tenant isolation, MVP vs v2 (+16 more)

### Community 97 - "CrmTool"
Cohesion: 0.16
Nodes (11): CrmTool, CRM business logic — called by MCP server only (Week 13 pattern)., mock_db(), fixture, CRM tool and tenant isolation tests., test_create_enrollment_rejects_cross_tenant_class(), test_create_enrollment_requires_consent(), test_get_tenant_info_returns_profile() (+3 more)

### Community 98 - "Database Patterns"
Cohesion: 0.09
Nodes (22): Alembic Migration Naming, Async Engine + Session, Bulk Insert, Bulk Operations, Bulk Update, Cascade Delete, Commit/Rollback Pattern, Constraint Naming (+14 more)

### Community 99 - "Dashboard API Contract (Phase 5)"
Cohesion: 0.09
Nodes (23): Dashboard API Contract (Phase 5), Endpoint map, Escalation inbox (unified HITL queue), Escalation object, Get thread (message panel), How to pass tenant, Integration flow (recommended), Legacy chat logs (+15 more)

### Community 100 - "models/__init__.py"
Cohesion: 0.09
Nodes (15): AuditLog, Base, Records all staff actions performed within the system., BankSlipUpload, Base, Represents a bank slip uploaded by a student for invoice verification., ParentGuardian, Base (+7 more)

### Community 101 - "run_chat_turn"
Cohesion: 0.17
Nodes (17): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, _routes_from_patch(), run_chat_turn(), RouteDecision (+9 more)

### Community 102 - "DriveTool"
Cohesion: 0.19
Nodes (12): DriveTool, Business logic for drive_search / drive_list — used by drive_server and REST., Drive MCP server — tool surface and tenant scoping (same logic as axiom-drive st, test_drive_mcp_list_folder(), test_drive_mcp_rejects_disallowed_folder(), test_drive_mcp_search_returns_link(), test_drive_mcp_tenant_isolation(), Drive tool unit tests. (+4 more)

### Community 103 - "MockDriveBackend"
Cohesion: 0.18
Nodes (9): build_drive_backend(), DriveBackend, GoogleDriveBackend, _prefer_ipv4_for_urllib3(), Any, Protocol, Google Drive client — service account, tenant-scoped folder search., Make urllib3/requests resolve A records only (AF_INET).      On dual-stack macOS (+1 more)

### Community 104 - "ResourceAgent"
Cohesion: 0.33
Nodes (7): FakeDrive, FakeRag, Any, asyncio, Resource agent node tests (direct tool clients, no MCP)., test_resource_agent_drive_path(), test_resource_agent_rag_path()

### Community 105 - "RagTool"
Cohesion: 0.15
Nodes (13): Any, RagTool, RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)., Business logic for kb_search — used by rag_server and debug REST., RAG MCP server — tool surface (same logic as axiom-rag stdio server)., test_rag_mcp_kb_ingest_status(), test_rag_mcp_kb_search_empty_collection(), test_rag_mcp_kb_search_with_citations() (+5 more)

### Community 106 - "rag_service.py"
Cohesion: 0.16
Nodes (13): BaseRetriever, Runnable, format_docs(), RAG helper utilities., Format LangChain documents into a single context block., build_rag_chain(), Config, Any (+5 more)

### Community 107 - "ChatChannel"
Cohesion: 0.44
Nodes (15): ChatChannel, EscalationStatus, ClassBase, ClassResponse, Config, EscalationCreate, EscalationResponse, InvoiceCreate (+7 more)

### Community 108 - "Demo UI Plan — WhatsApp Mock + Full Agent Lifecycle"
Cohesion: 0.11
Nodes (17): 10. Technical decisions, 11. Risks & mitigations, 12. Acceptance criteria, 13. Future (post-hackathon), 1. Product concept, 2. Folder structure, 3. BookMe AI → Axiom file mapping, 4. API integration (student chat) (+9 more)

### Community 109 - "models/enums.py"
Cohesion: 0.18
Nodes (11): Enrollment, Base, Represents a student's enrollment in a subject class., EnrollmentStatus, FeeCycle, Enum, str, StaffRole (+3 more)

### Community 110 - "routes/escalations.py"
Cohesion: 0.15
Nodes (13): Escalation, Base, Represents a conversation that requires manual intervention     from a staff mem, create_new_escalation(), get_escalations(), get_open_escalations(), get, post (+5 more)

### Community 111 - "get_conversation_thread"
Cohesion: 0.21
Nodes (16): _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_chat_turns(), get_conversation_thread(), get_thread_alias(), list_conversations(), Any (+8 more)

### Community 112 - "Phase 6 — Implementation Plan"
Cohesion: 0.12
Nodes (16): Acceptance criteria mapping, Explicitly out of scope (stay V2), Handoff checklist (dashboard team), Makefile targets (to add), Phase 6 — Implementation Plan, Risk register, Starting point (what’s already done), Suggested schedule (1 day) (+8 more)

### Community 113 - "MessagePersistence"
Cohesion: 0.15
Nodes (12): IdentityContext, Resolved tenant + student scope for one WhatsApp conversation., Resolved tenant scope; student_id is set only when a DB record exists., Stable recall key — student id when enrolled, otherwise phone., Past papers and RAG require pending or active enrollment., MessagePersistence, ChatChannel, MessageRole (+4 more)

### Community 114 - "dashboard/escalations.py"
Cohesion: 0.23
Nodes (15): _enrich_escalations(), EscalationActionResponse, list_escalations(), notify_student(), Any, BaseModel, DashboardTenant, get (+7 more)

### Community 115 - "map_decision_to_agent_state"
Cohesion: 0.28
Nodes (6): main(), _primary_route(), RoutingCase, _run(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, Decision subgraph state — separate from orchestrator AgentState.  Ported from Bo

### Community 116 - "MessageLog"
Cohesion: 0.15
Nodes (13): MessageLog, Base, Stores metadata about conversations between students and the AI assistant., create_message_log(), get_message_logs(), get, post, Session (+5 more)

### Community 117 - "test_tenant_scope.py"
Cohesion: 0.18
Nodes (12): Depends, Resolve tenant from query param or X-Tenant-ID header.      Dashboard frontend s, Ensure the tenant exists and is active before any dashboard handler runs., require_active_tenant(), resolve_tenant_id(), patch, Tenant scope validation for dashboard endpoints., test_require_active_tenant_not_found() (+4 more)

### Community 118 - "Axiom AI — Setup Guide (Phase 6)"
Cohesion: 0.13
Nodes (15): 10. Troubleshooting, 1. Prerequisites, 2. Clone and virtualenv, 3. Environment (`.env`), 4. Database, 5. Langfuse prompts, 6. RAG ingest (optional), 7. Run the API (+7 more)

### Community 119 - "QueryRouter"
Cohesion: 0.24
Nodes (6): _fallback_multi(), MultiRouteDecision, Any, QueryRouter, Attach I/O + usage to the current span/generation., update_current_observation()

### Community 120 - "escalation_reasons.py"
Cohesion: 0.22
Nodes (8): mock_db(), fixture, CRM escalation create/resolve tests for Phase 5 flows., test_create_payment_escalation(), test_create_talk_to_tutor_escalation(), test_reject_payment_escalation(), test_resolve_payment_escalation_activates_enrollment(), test_resolve_talk_to_tutor_does_not_activate_enrollment()

### Community 121 - "Quick Patterns"
Cohesion: 0.14
Nodes (13): Async Routes, Core Principles, Dependency Injection, Project Structure, Pydantic Validation, python-backend, Quick Patterns, Rate Limiting (+5 more)

### Community 122 - "memory.py"
Cohesion: 0.18
Nodes (9): MemEpisode, MemFact, MemProcedure, Base, Conversation summaries (episodic memory).      Each episode represents one summa, Short-term conversational memory.      Stores every conversation turn as a ring, Institution-level procedural memory.      Stores onboarding workflows, payment p, Long-term semantic memory for a specific student.      Stores distilled facts ex (+1 more)

### Community 123 - "EscalationAgent"
Cohesion: 0.15
Nodes (11): EscalationAgent, EscalationAgentResult, _last_user_text(), Escalation agent — talk-to-tutor requests → dashboard inbox., run_escalation_agent(), AgentState — shared LangGraph state for the Axiom orchestrator.  Ported from Boo, Escalation reason codes for dashboard inbox filtering., FakeCrm (+3 more)

### Community 124 - "router.py"
Cohesion: 0.20
Nodes (12): get_query_router(), heuristic_route(), _last_user_text(), _normalize_action(), _pattern_score(), Query Router — LLM intent classification for tuition agents.  Ported from BookMe, Deterministic routing for unambiguous tuition intents (before LLM)., router_node() (+4 more)

### Community 125 - "test_e2e_smoke.py"
Cohesion: 0.23
Nodes (8): _mock_oos_graph(), Any, asyncio, Fast E2E wiring tests (mocked LLM — BookMe / Week 13 decision_graph test pattern, Minimal stand-in — records whether orchestrator path runs (BookMe AI pattern)., _RecordingOrchestrator, test_in_scope_invokes_orchestrator(), test_out_of_scope_skips_orchestrator()

### Community 126 - "Sidebar.tsx"
Cohesion: 0.18
Nodes (7): DashboardLayoutProps, HeaderProps, NavItem, navItems, Sidebar(), SidebarProps, cn()

### Community 127 - "overview/page.tsx"
Cohesion: 0.22
Nodes (7): ChartCard(), ChartCardProps, MetricCard(), MetricCardProps, overviewMetrics, paymentTrends, studentGrowth

### Community 128 - "api.ts"
Cohesion: 0.23
Nodes (12): ChatLog, ChatTurn, Escalation, fakeDelay(), getChatLogs(), getEscalations(), getOverviewStats(), OverviewStats (+4 more)

### Community 129 - ".create_escalation"
Cohesion: 0.29
Nodes (4): Open (or return existing) escalation for dashboard inbox., Legacy alias — creates payment_receipt escalation without bank_slip storage., Staff rejects payment — closes escalation without activating enrollment., is_payment_reason()

### Community 130 - "routes/students.py"
Cohesion: 0.23
Nodes (9): Base, Represents a student registered under a tenant., Student, create_student(), get_student_by_phone(), get_students(), get, post (+1 more)

### Community 131 - "compilerOptions"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, moduleResolution, noEmit, skipLibCheck, strict, target (+3 more)

### Community 132 - "Phase 5 — Design Decisions (As Implemented)"
Cohesion: 0.17
Nodes (12): Acceptance criteria mapping, Agent ownership, Core decision: escalation-only HITL, Dashboard API (implemented), Decisions explicitly skipped, Flow 1 — Payment receipt, Flow 2 — Talk to tutor, Phase 5 — Design Decisions (As Implemented) (+4 more)

### Community 133 - "tenant_scope.py"
Cohesion: 0.23
Nodes (11): post, Staff reply to a student via WhatsApp.      Persists the message as role=system, send_staff_message(), assert_body_tenant(), assert_session_for_tenant(), Tenant scope validation for staff / dashboard endpoints., Resolved, active tenant — all dashboard queries must use this scope., Reject POST bodies whose tenant_id does not match the resolved scope. (+3 more)

### Community 134 - "SubjectClass"
Cohesion: 0.38
Nodes (6): create_class(), get_classes(), get, post, Session, ClassCreate

### Community 135 - "ShortTermMemoryStore"
Cohesion: 0.25
Nodes (4): ConversationTurn, Return up to k (user, assistant) pairs — BookMe SessionStore interface., Recent conversation turns per tenant/session., ShortTermMemoryStore

### Community 136 - "test_dashboard_api.py"
Cohesion: 0.35
Nodes (10): _chain_mock(), patch, Dashboard API HTTP tests (mocked Supabase + CRM)., test_dashboard_chat_conversations(), test_dashboard_chat_logs_alias(), test_dashboard_chat_thread(), test_dashboard_overview(), test_dashboard_staff_send_returns_turn() (+2 more)

### Community 137 - "turn_to_record"
Cohesion: 0.31
Nodes (9): ChatTurnRecord, Sender, build_conversation_summary(), phone_from_session_id(), Any, MessageRole, Shared helpers for dashboard chat endpoints., role_to_sender() (+1 more)

### Community 138 - "main"
Cohesion: 0.53
Nodes (8): _chat(), main(), _phone(), _require_live_env(), scenario_escalation(), scenario_onboarding(), scenario_payment(), scenario_resource_rag()

### Community 139 - "AGENTS.md — Axiom AI Backend"
Cohesion: 0.22
Nodes (8): AGENTS.md — Axiom AI Backend, Environment, Gotchas, Linting, LLM Providers, Project Structure, Quick Commands, Testing

### Community 140 - "health.py"
Cohesion: 0.36
Nodes (7): HealthResponse, active_config(), health(), get, Request, Health, readiness, and config endpoints., ready()

### Community 141 - "build_mcp_server_config"
Cohesion: 0.31
Nodes (8): step10b_mcp(), main(), _text(), build_mcp_server_config(), expected_mcp_tool_names(), mcp_include_drive(), MCP client configuration — memory + CRM + RAG (+ optional Drive).  Adapted from, Return config for ``MultiServerMCPClient`` (BookMe / Week 13 pattern).

### Community 142 - "Security Patterns"
Cohesion: 0.25
Nodes (7): API Key Auth via Header, CORS Configuration, FastAPI OAuth2 Bearer Dependency, Hide OpenAPI Docs by Default, JWT Create/Verify (python-jose), Password Hashing (passlib + bcrypt), Security Patterns

### Community 143 - "Demo UI — WhatsApp Student Chat"
Cohesion: 0.25
Nodes (7): Build, Demo UI — WhatsApp Student Chat, Env (optional), Features, Prerequisites, Project layout, Quick start

### Community 144 - "dashboard_overview"
Cohesion: 0.29
Nodes (7): _count_rows(), dashboard_overview(), Any, DashboardTenant, get, Dashboard overview stats for staff home screen., Aggregate counts for dashboard landing page.

### Community 145 - "PaymentStatusUpdate"
Cohesion: 0.29
Nodes (7): PaymentStatusUpdate, Example dashboard PATCH body using domain enums., parametrize, test_enum_values(), test_payment_status_update_accepts_enum(), test_payment_status_update_rejects_invalid(), test_tenant_summary_schema()

### Community 146 - "drive_server.py"
Cohesion: 0.36
Nodes (7): drive_list(), drive_search(), _init(), tool, Drive MCP Server — papers, textbooks, syllabus only., Search tenant Drive for papers, textbooks, or syllabus files. Returns shareable, List files in an allowed Drive subfolder (papers, textbooks, syllabus).

### Community 147 - "rag_server.py"
Cohesion: 0.36
Nodes (7): _init(), kb_ingest_status(), kb_search(), tool, RAG MCP Server — tenant-scoped tutor-note Q&A., Search tutor lesson notes (Qdrant) and return a grounded answer with citations., Return Qdrant ingest status for a tenant's tutor-note collection.

### Community 148 - "test_ingest_upload.py"
Cohesion: 0.25
Nodes (5): client(), fixture, patch, PDF ingest upload endpoint tests., test_ingest_upload_pdf()

### Community 149 - "app/layout.tsx"
Cohesion: 0.33
Nodes (4): geistMono, geistSans, metadata, ThemeInitializer()

### Community 150 - "Phase 5 — Escalations + staff chat"
Cohesion: 0.29
Nodes (7): Dashboard overview & chat logs, Escalations (payment + talk-to-tutor), Flow 1 — Payment receipt → dashboard inbox, Flow 2 — Talk to tutor, Phase 5 — Escalations + staff chat, Staff chat (dashboard integration), Staff reply

### Community 151 - "TwilioMessagingClient"
Cohesion: 0.16
Nodes (17): AnyMessage, GuardrailVerdict, map_decision_to_agent_state(), build_decision_graph(), build_decision_input(), make_guardrail_node(), DecisionState, TypedDict (+9 more)

### Community 152 - "get_chat_logs"
Cohesion: 0.29
Nodes (6): get_chat_logs(), ChatTurnsResponse, DashboardTenant, get, Dashboard chat history — legacy alias under /chat-logs., Legacy path for conversation history.      Prefer `GET /dashboard/chat/conversat

### Community 153 - "Demo script — Student chat only (~5 min)"
Cohesion: 0.33
Nodes (5): Demo script — Student chat only (~5 min), Narrative, Payment approval (outside this UI), Steps, Troubleshooting

### Community 154 - "list_classes"
Cohesion: 0.33
Nodes (5): list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant.

### Community 155 - "DriveResponse"
Cohesion: 0.18
Nodes (16): InfoInquiryKind, classify_info_inquiry(), extract_class_filters(), format_class_details(), _format_single_class(), format_staff_list(), format_tenant_info(), looks_like_institute_info() (+8 more)

### Community 156 - "upload_document"
Cohesion: 0.33
Nodes (5): post, Document ingest — PDF upload → parent-child chunk → Qdrant., Upload a tutor PDF, extract text, parent-child chunk, embed, and upsert to Qdran, upload_document(), UploadFile

### Community 157 - "supabase_client.py"
Cohesion: 0.33
Nodes (5): list_tenants(), ping_supabase(), Any, Supabase REST client wrapper., Lightweight connectivity check via tenants table.

### Community 158 - "test_router_intents.py"
Cohesion: 0.40
Nodes (5): asyncio, parametrize, Router intent classification tests., _router_with_content(), test_router_intents()

### Community 159 - "send_chat_message"
Cohesion: 0.29
Nodes (6): ChatRequest, ChatResponse, post, HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required)., Send a student message and receive an AI reply.      Use this during development, send_chat_message()

### Community 160 - "8. Implementation phases"
Cohesion: 0.40
Nodes (5): 8. Implementation phases, Phase A — Scaffold (~2h), Phase B — Student lifecycle (~2h), Phase C — Staff console (~2h), Phase D — Polish & docs (~1h)

### Community 161 - "test_merge_response.py"
Cohesion: 0.50
Nodes (4): asyncio, Merge response node tests., test_merge_multiple_fragments_uses_gemini(), test_merge_single_fragment_passthrough()

### Community 162 - "Axiom AI - Dashboard Backend"
Cohesion: 0.50
Nodes (3): Axiom AI - Dashboard Backend, Prerequisites, Setup Instructions

### Community 163 - "vite.config.ts"
Cohesion: 0.50
Nodes (3): __dirname, sharedDir, srcDir

### Community 164 - "test_run_resource_agent_requires_mcp_clients_when_fallback_disabled"
Cohesion: 0.50
Nodes (3): asyncio, Resource agent — in-process tools blocked when ALLOW_INPROCESS_TOOLS=false., test_run_resource_agent_requires_mcp_clients_when_fallback_disabled()

### Community 190 - "config.py"
Cohesion: 0.18
Nodes (12): get_chat_model(), get_embedding_model(), _get_nested(), get_role_config(), _get_str(), langfuse_configured(), _load_yaml(), Any (+4 more)

### Community 191 - "PaymentAgent"
Cohesion: 0.22
Nodes (10): _last_user_text(), PaymentAgent, PaymentAgentResult, Payment Check agent — payment receipt → escalation inbox., run_payment_agent(), FakeCrm, asyncio, Payment Check agent tests. (+2 more)

### Community 192 - "Path"
Cohesion: 0.18
Nodes (12): ChunkStrategy, Path, _mask_path(), step1_environment(), main(), load_tenant_docs(), Load markdown tutor notes and ingest (append — does not wipe collection)., Load markdown tutor notes from data/knowledge_base/{tenant_slug}/. (+4 more)

### Community 193 - "fixed_chunk"
Cohesion: 0.18
Nodes (12): fixed_chunk(), parent_child_chunk(), Any, Text chunking strategies — fixed + parent-child (Week 13 pattern)., Split documents into fixed-size chunks with overlap., Two-tier chunking: small child chunks indexed in Qdrant, parent text stored, patch, Ingest pipeline unit tests. (+4 more)

### Community 194 - "debug_drive_integration.py"
Cohesion: 0.29
Nodes (12): _list_children(), main(), _print_summary(), TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).  Does not, step12_network(), step2_auth(), step3_drive_client_direct(), step5_and_10_drive_tool() (+4 more)

### Community 195 - ".drive_list"
Cohesion: 0.19
Nodes (6): _normalize_drive_folder_id(), Any, Drive tool — tenant-scoped paper/textbook/syllabus search., Strip URL query junk users paste from Drive share links (e.g. ``?usp=drive_link`, Find subfolder ID (papers/textbooks/syllabus) under tenant root., resolve_subfolder_id()

### Community 196 - "IdentityResolver"
Cohesion: 0.35
Nodes (4): IdentityResolver, Any, Lookup tenant by sandbox number and student by sender phone., Resolve identity for HTTP dev chat when tenant_id is known.

### Community 197 - "test_chat.py"
Cohesion: 0.18
Nodes (7): chat_result(), client(), asyncio, fixture, HTTP dev chat endpoint tests., Regression: /chat must not call asyncio.run() inside FastAPI's event loop., test_chat_pipeline_runs_agent_inside_event_loop()

### Community 198 - "AdmissionsAgentResult"
Cohesion: 0.33
Nodes (4): AdmissionsAgentResult, _last_user_text(), Any, Admissions agent node — multi-turn onboarding via CRM MCP tools.

### Community 199 - "onboarding_route.py"
Cohesion: 0.29
Nodes (9): admissions_route_decision(), apply_onboarding_patch_overrides(), is_onboarding_active(), onboarding_router_context_hint(), Route-lock helpers — keep mid-onboarding turns on the admissions agent., True when a clear specialist intent should override active onboarding., True when an in-memory onboarding session is collecting details., Force proceed + admissions when mid-onboarding. Returns True if applied. (+1 more)

### Community 200 - "ingest_documents"
Cohesion: 0.36
Nodes (9): _build_parent_lookup(), embed_texts(), _enrich_children_with_parent_text(), ingest_documents(), Any, Tenant-scoped tutor-note ingestion into Qdrant., Extract text from PDF, parent-child chunk, embed, and upsert to Qdrant.     Opti, Chunk, embed, and upsert documents into the tenant Qdrant collection.      Paren (+1 more)

### Community 201 - "smoke_drive_paper_link"
Cohesion: 0.33
Nodes (8): main(), _mock_drive_backend(), Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)., Paper query → Drive link (mock backend; no Google credentials)., Velocity query → cited RAG answer (mocked RAG service)., smoke_drive_paper_link(), smoke_rag_velocity_live(), smoke_rag_velocity_mock()

### Community 203 - "MockDriveBackend"
Cohesion: 0.33
Nodes (7): MockDriveBackend, In-memory Drive mock for local dev and unit tests., chemistry_drive_backend(), physics_drive_backend(), fixture, mock_backend(), fixture

### Community 204 - "approve_payment"
Cohesion: 0.40
Nodes (6): approve_payment(), get_pending_payments(), get, Session, reject_payment(), put

### Community 205 - "log.py"
Cohesion: 0.40
Nodes (4): LogRecord, _InterceptHandler, Centralised loguru setup (stderr-only for future MCP safety)., setup_logging()

### Community 206 - "get_default_embeddings"
Cohesion: 0.33
Nodes (5): OpenAIEmbeddings, get_default_embeddings(), Any, OpenAI embeddings for RAG ingest and retrieval., Return configured embedding model (text-embedding-3-small by default).

### Community 207 - "smoke_mcp_memory.py"
Cohesion: 0.60
Nodes (5): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory()

### Community 208 - ".resolve_escalation"
Cohesion: 0.33
Nodes (3): Reason-aware resolve: payment → activate enrollment; tutor → close only., Staff approves payment — activates pending enrollment., Backward-compatible alias for payment resolve.

### Community 209 - "document_from_pdf"
Cohesion: 0.40
Nodes (5): document_from_pdf(), extract_pdf_text(), PDF text extraction for tutor document uploads., Extract plain text from a PDF byte stream., Build ingest document dict from uploaded PDF bytes.

### Community 210 - "test_config.py"
Cohesion: 0.33
Nodes (3): Config and tenant isolation unit tests., test_qdrant_collection_per_tenant(), test_validate_creates_directories()

### Community 211 - "smoke_resource.py"
Cohesion: 0.70
Nodes (4): main(), smoke_drive_mock(), smoke_ingest_load(), smoke_resource_agent()

### Community 212 - "get_summary"
Cohesion: 0.67
Nodes (3): get_summary(), get, Session

### Community 213 - "preload_agent_runtime"
Cohesion: 0.67
Nodes (3): preload_agent_runtime(), Any, Store warmed instances from FastAPI lifespan (BookMe AI ``main.py`` pattern).

## Knowledge Gaps
- **523 isolated node(s):** `eslintConfig`, `nextConfig`, `name`, `version`, `private` (+518 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CrmTool` connect `CrmTool` to `.create_escalation`, `Setup & Migration`, `._assert_tenant`, `.resolve_escalation`, `dashboard/escalations.py`, `7. Agentic AI Design`, `get_supabase_client`, `30. Learning Notes`, `escalation_reasons.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `IdentityContext` connect `MessagePersistence` to `IdentityResolver`, `Tasks`, `run_chat_turn`, `test_chat.py`, `3. Folder-by-Folder Explanation`, `IdentityContext`, `Chat Flow`, `TwilioMessagingClient`, `test_e2e_smoke.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `EscalationActionResponse` connect `dashboard/escalations.py` to `CrmTool`, `Infrastructure Support`, `IdentityResolver`, `Tasks`, `ChatChannel`, `MessagePersistence`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `OnboardingFlow` (e.g. with `main()` and `AdmissionsAgent`) actually correct?**
  _`OnboardingFlow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `AgentState` (e.g. with `AdmissionsAgent` and `AdmissionsAgentResult`) actually correct?**
  _`AgentState` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `get_supabase_client()` (e.g. with `main()` and `step6_tenant()`) actually correct?**
  _`get_supabase_client()` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `IdentityContext` (e.g. with `main()` and `main()`) actually correct?**
  _`IdentityContext` has 17 INFERRED edges - model-reasoned connections that need verification._