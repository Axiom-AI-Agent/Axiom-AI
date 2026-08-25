# Graph Report - Axiom-AI  (2026-08-25)

## Corpus Check
- 325 files · ~459,484 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2861 nodes · 5376 edges · 235 communities (199 shown, 36 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 912 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `80796f3f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Admissions Onboarding
- Admissions Onboarding 2
- Demo Chat Lifecycle
- RAG Ingest Pipeline
- Admissions Onboarding 3
- RAG Ingest Pipeline 2
- Dashboard Frontend Pages
- RAG Ingest Pipeline 3
- Student Chat Deps
- RAG Ingest Pipeline 4
- Student Chat Deps 2
- Student Chat Deps 3
- Admissions Onboarding 4
- Design Double Diamond
- Design Double Diamond 2
- Admissions Onboarding 5
- Dashboard Frontend Deps
- Admissions Onboarding 6
- Drive Tooling
- API Chat Schemas
- Design Double Diamond 3
- Decision Graph
- Dashboard ORM Models
- Admissions Onboarding 7
- Agent Orchestrator
- Admissions Onboarding 8
- Drive Tooling 2
- Supabase DB Client
- Agent Orchestrator 2
- Drive Tooling 3
- Identity Context
- Admissions Onboarding 9
- Admissions Onboarding 10
- Resource Agent
- Chat Message Pipeline
- Invoice DB Layer
- Design Double Diamond 4
- RAG Ingest Pipeline 5
- Escalation Routes
- Chat Message Pipeline 2
- Invoice DB Layer 2
- Chat Message Pipeline 3
- Dashboard ORM Models 2
- Decision Graph 2
- Escalation Routes 2
- Dashboard Module
- Invoice DB Layer 3
- CRM MCP Server
- Escalation Routes 3
- Langfuse Runtime
- Langfuse Runtime 2
- Test Suite
- Agent Orchestrator 3
- Admissions Onboarding 11
- Workshop Exploration
- Admissions Onboarding 12
- Supabase DB Client 2
- Langfuse Runtime 3
- Decision Graph 3
- Test Suite 2
- Student Chat Deps 4
- Workshop Exploration 2
- RAG Tooling
- CRM MCP Server 2
- Student Chat Deps 5
- Test Suite 3
- IdentityResolver
- Chat Message Pipeline 4
- Chat Turn Runner
- Langfuse Runtime 4
- MCP Integration
- Dashboard API Routes
- Escalation Routes 4
- Memory MCP Path
- Supabase DB Client 3
- Dashboard Module 2
- Admissions Onboarding 13
- infrastructure config py
- Langfuse Runtime 5
- Admissions Onboarding 14
- Admissions Onboarding 15
- Escalation Routes 5
- Escalation Routes 6
- Escalation Routes 7
- Drive Tooling 4
- Resource Agent 2
- Dashboard Module 3
- Dashboard API Routes 2
- MCP Integration 2
- Test Suite 4
- Test Suite 5
- Design Double Diamond 5
- Escalation Routes 8
- Escalation Routes 9
- Escalation Routes 10
- Dashboard Module 4
- Escalation Routes 11
- Demo Chat Lifecycle 2
- Admissions Onboarding 16
- Escalation Routes 12
- Dashboard Module 5
- Test Suite 6
- Admissions Onboarding 17
- MCP Integration 3
- Admissions Onboarding 18
- Escalation Routes 13
- Dashboard API Routes 3
- MCP Integration 4
- RAG Ingest Pipeline 6
- Supabase DB Client 5
- Test Suite 7
- Dashboard Module 6
- RAG Ingest Pipeline 7
- Chat Message Pipeline 5
- Langfuse Runtime 6
- Dashboard Module 7
- Dashboard Module 8
- Student Chat Deps 6
- Demo Chat Lifecycle 3
- Chat Message Pipeline 6
- MCP Integration 5
- verify phase0 py
- Resource Agent 3
- Dashboard Frontend Deps 2
- Dashboard Module 9
- Dashboard Module 10
- Dashboard Module 11
- Dashboard API Routes 4
- Student Chat Deps 7
- Decision Graph 4
- Supabase DB Client 6
- Smoke Scripts
- preload agent runtime
- Password Hashing
- MESSAGING DRY RUN
- Dashboard Frontend Deps 3
- Dashboard Module 12
- Dashboard Frontend Deps 4
- Dashboard Module 13
- Dashboard Module 14
- Dashboard Module 15
- Dashboard Module 16
- Dashboard Module 17
- Student Chat Deps 8
- Demo UI
- Langfuse Runtime 7
- LangGraph Supervisor Orchestrator
- Sri Lankan Private
- check python py
- Admissions Onboarding 19
- Langfuse Runtime 8
- Langfuse Runtime 9
- Dashboard Module 18
- Escalation Routes 14
- run py
- llm init py
- src init py
- Admissions Onboarding 20
- identity init py
- Chat Message Pipeline 7
- Return the latest
- rag templates py
- Demo UI 2
- Demo UI 3
- AI Tutor SaaS
- OpenRouter LLM Access
- axiom ai backend
- agents tools init
- api init py
- routers init py
- routers tools init
- Twilio Webhook
- db init py
- MCP Integration 6
- memory init py
- drive service init
- ingest service init
- src services init
- services prompts init
- rag service init
- mockData.ts
- overview.ts
- Dashboard Alembic Dependency
- AI_API_BASE
- DASHBOARD_API_BASE
- Axiom AI Backend (README)
- MCP Adapters
- RateLimitMiddleware
- tenant_scope.py
- validate
- FakeCrm
- Phase 5 — Escalations + staff chat
- ._assert_tenant
- FakeCrm
- get_default_embeddings
- log.py
- test_run_resource_agent_requires_mcp_clients_when_fallback_disabled
- register_telegram_webhook.py
- main
- _load_env
- main
- admissions_db_client.py
- .resolve_escalation
- test_merge_response.py
- document_from_pdf
- 8. Implementation phases
- test_routing_smoke.py
- _one_turn

## God Nodes (most connected - your core abstractions)
1. `get_supabase_client()` - 60 edges
2. `OnboardingFlow` - 54 edges
3. `AgentState` - 53 edges
4. `IdentityContext` - 45 edges
5. `CrmTool` - 40 edges
6. `ChatChannel` - 39 edges
7. `RagTool` - 36 edges
8. `CrmClient` - 35 edges
9. `DirectCrmClient` - 33 edges
10. `ResourceAgent` - 33 edges

## Surprising Connections (you probably didn't know these)
- `Tenant` --uses--> `TenantStatus`  [INFERRED]
  Dashboard/backend/app/models/tenant.py → AI-backend/src/domain/enums.py
- `Enrollment` --uses--> `EnrollmentStatus`  [INFERRED]
  Dashboard/backend/app/models/enrollment.py → AI-backend/src/domain/enums.py
- `EscalationResponse` --uses--> `EnrollmentStatus`  [INFERRED]
  Dashboard/backend/app/schemas/schemas.py → AI-backend/src/domain/enums.py
- `Invoice` --uses--> `InvoiceStatus`  [INFERRED]
  Dashboard/backend/app/models/invoice.py → AI-backend/src/domain/enums.py
- `Escalation` --uses--> `EscalationStatus`  [INFERRED]
  Dashboard/backend/app/models/escalation.py → AI-backend/src/domain/enums.py

## Import Cycles
- None detected.

## Communities (235 total, 36 thin omitted)

### Community 0 - "Admissions Onboarding"
Cohesion: 0.08
Nodes (24): OnboardingFlow, OnboardingSlots, Any, Multi-turn admissions onboarding — slot tracking and class disambiguation., Determine onboarding progress and extract slots from user messages., Hydrate state for an existing database student (post-enrollment paths only)., Onboarding flow unit tests., test_awaiting_review_state() (+16 more)

### Community 1 - "Admissions Onboarding 2"
Cohesion: 0.21
Nodes (18): AdmissionsAgent, get_onboarding_session_store(), clear_onboarding_sessions(), FakeCrmClient, asyncio, fixture, Admissions agent node tests (in-process CRM, no MCP subprocess)., _state() (+10 more)

### Community 2 - "Demo Chat Lifecycle"
Cohesion: 0.10
Nodes (9): CrmClient, DirectCrmClient, McpCrmClient, Any, Protocol, Shared CRM client protocol for agent nodes (direct + MCP paths)., MCP CRM tools → async dispatch., In-process CRM path (dev/tests without MCP subprocesses). (+1 more)

### Community 3 - "RAG Ingest Pipeline"
Cohesion: 0.24
Nodes (16): qdrant_collection_for_tenant(), collection_exists(), collection_info(), count_points(), delete_collection(), ensure_class_id_index(), ensure_collection(), get_qdrant_client() (+8 more)

### Community 4 - "Admissions Onboarding 3"
Cohesion: 0.06
Nodes (45): ApiError, BASE, chatApi, systemApi, App(), ChatWindow(), Props, DemoProgress() (+37 more)

### Community 5 - "RAG Ingest Pipeline 2"
Cohesion: 0.08
Nodes (39): main(), build_orchestrator(), In-process MemoryTool path (dev/tests without MCP subprocesses)., get_api_key(), get_chat_model(), get_embedding_model(), _get_nested(), get_role_config() (+31 more)

### Community 6 - "Dashboard Frontend Pages"
Cohesion: 0.07
Nodes (38): ClassFormState, emptyForm, ApiError, approvePayment(), assignEscalation(), ChatConversation, ChatSender, ChatThread (+30 more)

### Community 7 - "RAG Ingest Pipeline 3"
Cohesion: 0.14
Nodes (14): format_docs(), RAG helper utilities., Format LangChain documents into a single context block., build_rag_chain(), Config, Any, RAGService, Plain RAG service — Qdrant retrieval + Gemini synthesis (no CAG/CRAG). (+6 more)

### Community 8 - "Student Chat Deps"
Cohesion: 0.04
Nodes (44): dependencies, clsx, framer-motion, lucide-react, react, react-dom, react-markdown, remark-gfm (+36 more)

### Community 9 - "RAG Ingest Pipeline 4"
Cohesion: 0.50
Nodes (4): Dashboard FastAPI Dependency, pgvector, Dashboard SQLAlchemy Dependency, Dashboard Backend

### Community 10 - "Student Chat Deps 2"
Cohesion: 0.05
Nodes (40): chart.js, dependencies, chart.js, framer-motion, lucide-react, next, react, react-chartjs-2 (+32 more)

### Community 11 - "Student Chat Deps 3"
Cohesion: 0.06
Nodes (36): Application Access Patterns, Apply schema, `audit_logs` (AUDIT_LOG), Axiom AI — Database Documentation, `bank_slip_uploads` (BANK_SLIP_UPLOAD), Demo Seed Data, `enrollments` (ENROLLMENT), ENUM Types (+28 more)

### Community 12 - "Admissions Onboarding 4"
Cohesion: 0.10
Nodes (28): run_admissions_agent(), EscalationAgentResult, _last_user_text(), Escalation agent — talk-to-tutor requests → dashboard inbox., run_escalation_agent(), _last_user_text(), PaymentAgent, PaymentAgentResult (+20 more)

### Community 13 - "Design Double Diamond"
Cohesion: 0.06
Nodes (33): Agent pipeline, Axiom AI Backend — Finalize Checklist, Bot & environment, Core agent & routing, Dashboard handoff, Demo UI (`demo-ui-org/`), Documentation, Documentation sync (+25 more)

### Community 14 - "Design Double Diamond 2"
Cohesion: 0.14
Nodes (21): AuthContext, AuthContextValue, AuthProvider(), request(), AuthApiError, authRequest(), getMe(), loginStaff() (+13 more)

### Community 15 - "Admissions Onboarding 5"
Cohesion: 0.27
Nodes (28): ChatConversationsResponse, ChatConversationSummary, ChatRequest, ChatResponse, ChatThreadResponse, ChatTurnRecord, ChatTurnsResponse, ConfigResponse (+20 more)

### Community 16 - "Dashboard Frontend Deps"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "Admissions Onboarding 6"
Cohesion: 0.12
Nodes (29): commit_onboarding(), create_enrollment(), create_escalation(), get_class_details(), get_student(), get_tenant_info(), _init(), list_classes() (+21 more)

### Community 18 - "Drive Tooling"
Cohesion: 0.19
Nodes (5): get_supabase_client(), Return a singleton Supabase client (requires service role key)., AdmissionsDbClient, Any, Tenant-scoped student, class, and enrollment persistence.

### Community 19 - "API Chat Schemas"
Cohesion: 0.18
Nodes (10): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory(), build_agent_mcp(), _MCPMemoryToolAdapter, MCP memory tools → async dispatch (Week 13 / BookMe MCP adapter pattern). (+2 more)

### Community 20 - "Design Double Diamond 3"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+16 more)

### Community 21 - "Decision Graph"
Cohesion: 0.14
Nodes (13): CrmTool, CRM business logic — called by MCP server only (Week 13 pattern)., mock_db(), fixture, CRM tool and tenant isolation tests., test_commit_onboarding_completes_unenrolled_profile(), test_commit_onboarding_rejects_already_enrolled(), test_create_enrollment_rejects_cross_tenant_class() (+5 more)

### Community 22 - "Dashboard ORM Models"
Cohesion: 0.06
Nodes (24): AuditLog, Base, Records all staff actions performed within the system., BankSlipUpload, Base, Represents a bank slip uploaded by a student for invoice verification., Invoice, Base (+16 more)

### Community 23 - "Admissions Onboarding 7"
Cohesion: 0.05
Nodes (41): DriveTool, _normalize_drive_folder_id(), Any, Drive tool — tenant-scoped paper/textbook/syllabus search., Strip URL query junk users paste from Drive share links (e.g. ``?usp=drive_link`, Business logic for drive_search / drive_list — used by drive_server and REST., drive_list(), drive_search() (+33 more)

### Community 24 - "Agent Orchestrator"
Cohesion: 0.18
Nodes (13): main(), ChatPipeline, Channel-agnostic chat pipeline — HTTP dev chat + Twilio webhook., Sync entry for scripts and tests without a running event loop., ChatTurnResult, InboundMessage, BaseModel, Messaging payload schemas — Twilio + channel-agnostic chat. (+5 more)

### Community 25 - "Admissions Onboarding 8"
Cohesion: 0.08
Nodes (25): API Design, Async Routes, Async Test Client from Day 0, Chain Dependencies, CPU Intensive Tasks, Custom Base Model, Decouple BaseSettings, Dependencies (+17 more)

### Community 26 - "Drive Tooling 2"
Cohesion: 0.22
Nodes (13): ClassesPage(), IngestContent(), MessagesContent(), senderBubbleClass(), TenantSelector(), useTenant(), useToast(), aiRequest() (+5 more)

### Community 27 - "Supabase DB Client"
Cohesion: 0.08
Nodes (23): Basic Setup, Batch Messages, Best Practices, FastAPI Caching, FastAPI Rate Limiting, FastAPI Session Management, Hash Operations, Key Expiration (TTL) (+15 more)

### Community 28 - "Agent Orchestrator 2"
Cohesion: 0.08
Nodes (24): 1. Google Cloud, 2. Environment, Architecture, Folder ID, Folder layout, Google Drive MCP — Integration & Testing, Multi-tenant isolation, MVP vs v2 (+16 more)

### Community 29 - "Drive Tooling 3"
Cohesion: 0.20
Nodes (7): MessagePersistence, ChatChannel, MessageRole, Persist inbound/outbound messaging to Supabase (message_logs + st_turns)., Return the latest turn per session_id, ordered by most recent activity., Write message_logs and st_turns rows for a conversation turn., Persist a staff-authored message (role=system → sender=staff in dashboard UI).

### Community 30 - "Identity Context"
Cohesion: 0.09
Nodes (22): Alembic Migration Naming, Async Engine + Session, Bulk Insert, Bulk Operations, Bulk Update, Cascade Delete, Commit/Rollback Pattern, Constraint Naming (+14 more)

### Community 31 - "Admissions Onboarding 9"
Cohesion: 0.12
Nodes (22): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, _routes_from_patch(), run_chat_turn(), classify_confirmation() (+14 more)

### Community 32 - "Admissions Onboarding 10"
Cohesion: 0.14
Nodes (14): build_decision_graph(), _emit_from_config(), make_guardrail_node(), make_router_node(), EmitFn, RunnableConfig, Decision LangGraph — guardrail and router subgraph for Axiom AI.  Ported from Bo, _build_user_prompt() (+6 more)

### Community 33 - "Resource Agent"
Cohesion: 0.13
Nodes (16): DashboardLayoutProps, ProtectedDashboard(), Header(), HeaderProps, ToastContainer(), toastStyles(), useAuth(), TenantContext (+8 more)

### Community 34 - "Chat Message Pipeline"
Cohesion: 0.18
Nodes (7): parse_twilio_form(), Parse Twilio application/x-www-form-urlencoded webhook bodies., client(), identity_ctx(), fixture, Twilio webhook endpoint tests., test_parse_twilio_form_extracts_media()

### Community 35 - "Invoice DB Layer"
Cohesion: 0.07
Nodes (27): get_db(), get_tenant_id(), Authenticated tenant scope for dashboard API requests., get, root(), MessageLog, Base, Stores metadata about conversations between students and the AI assistant. (+19 more)

### Community 36 - "Design Double Diamond 4"
Cohesion: 0.16
Nodes (17): InboxContent(), isPaymentReason(), statusClass(), EscalationSocketEvent, EscalationSocketEventType, useEscalationSocket(), UseEscalationSocketOptions, usePolling() (+9 more)

### Community 37 - "RAG Ingest Pipeline 5"
Cohesion: 0.14
Nodes (13): Any, RagTool, RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)., Business logic for kb_search — used by rag_server and debug REST., RAG MCP server — tool surface (same logic as axiom-rag stdio server)., test_rag_mcp_kb_ingest_status(), test_rag_mcp_kb_search_empty_collection(), test_rag_mcp_kb_search_with_citations() (+5 more)

### Community 38 - "Escalation Routes"
Cohesion: 0.35
Nodes (13): assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get_tenant_escalation_or_404(), Escalation, get, post (+5 more)

### Community 39 - "Chat Message Pipeline 2"
Cohesion: 0.29
Nodes (9): FakeDrive, FakeRag, asyncio, Identity recall and resource enrollment gate tests., test_identity_resolver_keeps_enrolled_student(), test_identity_resolver_treats_unenrolled_row_as_visitor(), test_resource_agent_allows_pending_enrollment(), test_resource_agent_blocks_non_enrolled_drive() (+1 more)

### Community 40 - "Invoice DB Layer 2"
Cohesion: 0.29
Nodes (30): ChatChannel, EnrollmentStatus, EscalationStatus, ClassBase, ClassCreate, ClassResponse, ClassUpdate, Config (+22 more)

### Community 41 - "Chat Message Pipeline 3"
Cohesion: 0.17
Nodes (19): main(), scenario_out_of_scope(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), preload_agent_runtime(), Any, Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline. (+11 more)

### Community 42 - "Dashboard ORM Models 2"
Cohesion: 0.10
Nodes (33): get_current_staff(), Session, Base, Represents a staff member of a tuition institute., StaffUser, bootstrap_demo_physics(), login(), me() (+25 more)

### Community 43 - "Decision Graph 2"
Cohesion: 0.17
Nodes (19): _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_chat_turns(), get_conversation_thread(), get_thread_alias(), list_conversations(), Any (+11 more)

### Community 44 - "Escalation Routes 2"
Cohesion: 0.17
Nodes (12): Architecture, Dev Chat — WhatsApp Simulator (No Twilio Required), Endpoints, Fetch conversation history, Prerequisites, Reference implementations, Related docs, Request body (+4 more)

### Community 45 - "Dashboard Module"
Cohesion: 0.39
Nodes (7): get_tenant_profile(), list_tenants(), _normalize_slug(), get, put, Session, update_tenant_profile()

### Community 46 - "Invoice DB Layer 3"
Cohesion: 0.11
Nodes (17): 10. Technical decisions, 11. Risks & mitigations, 12. Acceptance criteria, 13. Future (post-hackathon), 1. Product concept, 2. Folder structure, 3. BookMe AI → Axiom file mapping, 4. API integration (student chat) (+9 more)

### Community 47 - "CRM MCP Server"
Cohesion: 0.20
Nodes (17): build_direct_system_prompt(), build_escalation_ack_reply(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply(), build_resource_drive_reply(), build_resource_rag_reply() (+9 more)

### Community 48 - "Escalation Routes 3"
Cohesion: 0.20
Nodes (14): emptyForm, matchesStudentSearch(), ModalMode, StudentsPage(), EnrollModal(), EnrollModalProps, StudentFormModal(), StudentFormModalProps (+6 more)

### Community 49 - "Langfuse Runtime"
Cohesion: 0.08
Nodes (25): Dashboard API Contract (Phase 5), Document ingest (knowledge base), Endpoint map, Escalation inbox (unified HITL queue), Escalation object, Get thread (message panel), How to pass tenant, Integration flow (recommended) (+17 more)

### Community 50 - "Langfuse Runtime 2"
Cohesion: 0.13
Nodes (17): main(), main(), get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session., session_id_for_phone(), build_session_id() (+9 more)

### Community 51 - "Test Suite"
Cohesion: 0.11
Nodes (22): _chain_mock(), main(), assert_body_tenant(), assert_session_for_tenant(), Tenant scope validation for staff / dashboard endpoints., Resolved, active tenant — all dashboard queries must use this scope., Resolve tenant from query param or X-Tenant-ID header.      Dashboard frontend s, Ensure the tenant exists and is active before any dashboard handler runs. (+14 more)

### Community 52 - "Agent Orchestrator 3"
Cohesion: 0.12
Nodes (16): Acceptance criteria mapping, Explicitly out of scope (stay V2), Handoff checklist (dashboard team), Makefile targets (to add), Phase 6 — Implementation Plan, Risk register, Starting point (what’s already done), Suggested schedule (1 day) (+8 more)

### Community 53 - "Admissions Onboarding 11"
Cohesion: 0.28
Nodes (5): _fallback_multi(), MultiRouteDecision, Any, QueryRouter, test_router_parses_json_routes()

### Community 54 - "Workshop Exploration"
Cohesion: 0.23
Nodes (15): _enrich_escalations(), EscalationActionResponse, list_escalations(), notify_student(), Any, BaseModel, DashboardTenant, get (+7 more)

### Community 55 - "Admissions Onboarding 12"
Cohesion: 0.20
Nodes (8): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Support Langfuse `{{var}}` and local `{var}` placeholders., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 56 - "Supabase DB Client 2"
Cohesion: 0.13
Nodes (15): 10. Troubleshooting, 1. Prerequisites, 2. Clone and virtualenv, 3. Environment (`.env`), 4. Database, 5. Langfuse prompts, 6. RAG ingest (optional), 7. Run the API (+7 more)

### Community 57 - "Langfuse Runtime 3"
Cohesion: 0.22
Nodes (8): mock_db(), fixture, CRM escalation create/resolve tests for Phase 5 flows., test_create_payment_escalation(), test_create_talk_to_tutor_escalation(), test_reject_payment_escalation(), test_resolve_payment_escalation_activates_enrollment(), test_resolve_talk_to_tutor_does_not_activate_enrollment()

### Community 58 - "Decision Graph 3"
Cohesion: 0.17
Nodes (21): clear_bot_token_cache(), _fetch_tenant_bot_row(), get_bot_token_for_tenant(), Any, Per-tenant Telegram bot token lookup (SRS NFR-17 — not env vars)., Raised when a tenant has no usable Telegram bot token., Drop cached tokens — used by tests and after rotating a token., Return the Telegram bot token for ``tenant_id``.      Tokens are stored on ``ten (+13 more)

### Community 59 - "Test Suite 2"
Cohesion: 0.17
Nodes (17): map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, build_decision_input(), decide_node(), Any, DecisionState, TypedDict, Decision subgraph state — separate from orchestrator AgentState.  Ported from Bo (+9 more)

### Community 60 - "Student Chat Deps 4"
Cohesion: 0.13
Nodes (17): main(), smoke_drive_mock(), smoke_ingest_load(), smoke_resource_agent(), fixed_chunk(), parent_child_chunk(), Any, Text chunking strategies — fixed + parent-child (Week 13 pattern). (+9 more)

### Community 61 - "Workshop Exploration 2"
Cohesion: 0.23
Nodes (15): _build_parent_lookup(), embed_texts(), _enrich_children_with_parent_text(), ingest_documents(), load_tenant_docs(), Any, Tenant-scoped tutor-note ingestion into Qdrant., Chunk, embed, and upsert documents into the tenant Qdrant collection.      Paren (+7 more)

### Community 62 - "RAG Tooling"
Cohesion: 0.14
Nodes (13): Async Routes, Core Principles, Dependency Injection, Project Structure, Pydantic Validation, python-backend, Quick Patterns, Rate Limiting (+5 more)

### Community 63 - "CRM MCP Server 2"
Cohesion: 0.17
Nodes (18): Base, Represents a student registered under a tenant., Student, create_student(), delete_student(), enroll_student(), get_student(), get_student_by_phone() (+10 more)

### Community 64 - "Student Chat Deps 5"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, moduleResolution, noEmit, skipLibCheck, strict, target (+3 more)

### Community 65 - "Test Suite 3"
Cohesion: 0.12
Nodes (16): IdentityContext, Resolved tenant + student scope for one WhatsApp conversation., Resolved tenant scope; student_id is set only when a DB record exists., Stable recall key — student id when enrolled, otherwise phone., Past papers and RAG require pending or active enrollment., build_recall_context(), format_student_profile(), Build recall context (student profile + ST turns) before the decision graph. (+8 more)

### Community 66 - "IdentityResolver"
Cohesion: 0.14
Nodes (17): _parse_form_params(), post, Request, Response, Twilio WhatsApp webhook router., Twilio WhatsApp sandbox webhook.      Returns 200 immediately and processes the, _should_validate_signature(), twilio_webhook() (+9 more)

### Community 67 - "Chat Message Pipeline 4"
Cohesion: 0.11
Nodes (10): Memory business logic — called by MCP server only (Week 13 pattern)., ProceduralMemoryStore, Procedural memory store — tenant-scoped ``mem_procedures`` lookup.  Adapted from, ConversationTurn, Procedure, Memory schemas — ported from Week 13 ``memory/schemas.py`` (MVP subset)., Short-term memory store — Supabase ``st_turns`` ring buffer.  Adapted from Week, Return up to k (user, assistant) pairs — BookMe SessionStore interface. (+2 more)

### Community 68 - "Chat Turn Runner"
Cohesion: 0.19
Nodes (12): Propagate tenant/session/user identifiers to all nested Langfuse observations., Langfuse trace scope for a WhatsApp conversation turn., Test helper — clear cached Langfuse client state., reset_langfuse_state(), trace_context(), TraceContext, Observability helper tests., setup_function() (+4 more)

### Community 69 - "Langfuse Runtime 4"
Cohesion: 0.20
Nodes (16): _disable_langfuse(), get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), prefetch_prompts(), BaseException, Langfuse observability — tracing per tenant/session/user and prompt hooks.  Prom (+8 more)

### Community 70 - "MCP Integration"
Cohesion: 0.13
Nodes (15): get_drive_tool(), get_rag_tool(), get_request_id(), Request, FastAPI dependency injection helpers., _require_startup(), list_files(), post (+7 more)

### Community 71 - "Dashboard API Routes"
Cohesion: 0.16
Nodes (15): Base, Represents a tuition class offered by a tenant., SubjectClass, create_class(), delete_class(), get_class(), get_classes(), _parse_fee_cycle() (+7 more)

### Community 72 - "Escalation Routes 4"
Cohesion: 0.14
Nodes (22): Escalation, Base, Represents a conversation that requires manual intervention     from a staff mem, assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get_tenant_escalation_or_404() (+14 more)

### Community 73 - "Memory MCP Path"
Cohesion: 0.29
Nodes (12): _list_children(), main(), _print_summary(), TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).  Does not, step12_network(), step2_auth(), step3_drive_client_direct(), step5_and_10_drive_tool() (+4 more)

### Community 74 - "Supabase DB Client 3"
Cohesion: 0.18
Nodes (16): classify_info_inquiry(), extract_class_filters(), format_class_details(), _format_single_class(), format_staff_list(), format_tenant_info(), looks_like_institute_info(), Any (+8 more)

### Community 75 - "Dashboard Module 2"
Cohesion: 0.31
Nodes (9): build_conversation_summary(), phone_from_session_id(), Any, MessageRole, Shared helpers for dashboard chat endpoints., role_to_sender(), turn_to_record(), ChatTurnRecord (+1 more)

### Community 76 - "Admissions Onboarding 13"
Cohesion: 0.17
Nodes (12): Acceptance criteria mapping, Agent ownership, Core decision: escalation-only HITL, Dashboard API (implemented), Decisions explicitly skipped, Flow 1 — Payment receipt, Flow 2 — Talk to tutor, Phase 5 — Design Decisions (As Implemented) (+4 more)

### Community 77 - "infrastructure config py"
Cohesion: 0.17
Nodes (12): 16.10 V2 Architecture Upgrades (Reference Patterns), 16.11 V2 Acceptance Themes, 16.1 Messaging & Infrastructure, 16.2 AI Agents & Orchestration, 16.3 Memory, Caching & RAG Enhancements, 16.4 Payments & Finance Automation, 16.5 Integrations & Tooling, 16.6 CRM, Dashboard & Backend APIs (Extended) (+4 more)

### Community 78 - "Langfuse Runtime 5"
Cohesion: 0.20
Nodes (17): download_telegram_file(), get_telegram_file_path(), Any, Response, _raise_telegram_error(), Thin Telegram Bot API client — one token per tenant, never a global token., Send a plain text message to a Telegram chat using that tenant's bot token., Send a message with a one-time 'Share phone number' keyboard. (+9 more)

### Community 79 - "Admissions Onboarding 14"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 80 - "Admissions Onboarding 15"
Cohesion: 0.20
Nodes (12): get_query_router(), heuristic_route(), _last_user_text(), _normalize_action(), _pattern_score(), Query Router — LLM intent classification for tuition agents.  Ported from BookMe, Deterministic routing for unambiguous tuition intents (before LLM)., router_node() (+4 more)

### Community 81 - "Escalation Routes 5"
Cohesion: 0.20
Nodes (6): OnboardingState, OnboardingSession, OnboardingSessionStore, In-memory onboarding session store — Week 13 SessionStore pattern.  Onboarding s, Ephemeral multi-turn onboarding progress for one tenant+phone pair., Process-local store keyed by ``tenant_id:phone``.

### Community 82 - "Escalation Routes 6"
Cohesion: 0.18
Nodes (8): chat_result(), client(), asyncio, fixture, HTTP dev chat endpoint tests., Regression: /chat must not call asyncio.run() inside FastAPI's event loop., test_chat_pipeline_runs_agent_inside_event_loop(), test_chat_unknown_tenant_returns_404()

### Community 83 - "Escalation Routes 7"
Cohesion: 0.22
Nodes (11): FakeDrive, Any, asyncio, patch, Class-scoped RAG retrieval tests., test_kb_search_forwards_class_ids_to_rag_service(), test_resource_agent_blocks_enrolled_without_class_ids(), test_resource_agent_passes_enrolled_class_ids_to_rag() (+3 more)

### Community 84 - "Drive Tooling 4"
Cohesion: 0.22
Nodes (10): _mock_oos_graph(), _mock_proceed_graph(), Any, asyncio, Fast E2E wiring tests (mocked LLM — BookMe / Week 13 decision_graph test pattern, Minimal stand-in — records whether orchestrator path runs (BookMe AI pattern)., _RecordingOrchestrator, test_in_scope_invokes_orchestrator() (+2 more)

### Community 85 - "Resource Agent 2"
Cohesion: 0.10
Nodes (19): classify_resource_subpath(), DriveClient, _infer_drive_folder(), _last_user_text(), _mcp_text(), McpDriveClient, McpRagClient, Any (+11 more)

### Community 86 - "Dashboard Module 3"
Cohesion: 0.18
Nodes (9): _mask_path(), step1_environment(), main(), main(), TEMP DEBUG — Google OAuth only (no Drive list, no MCP).  Run:   PYTHONPATH=src ., test_register_webhook_url_includes_tenant_path(), _load_env(), Load env from Dashboard, shared AI-backend, or repo root. (+1 more)

### Community 87 - "Dashboard API Routes 2"
Cohesion: 0.27
Nodes (9): RouteDecision, clear_onboarding_sessions(), ctx(), asyncio, fixture, Onboarding route lock tests., test_active_onboarding_forces_admissions_route(), test_onboarding_bypasses_guardrail_oos_on_confirm_yes() (+1 more)

### Community 88 - "MCP Integration 2"
Cohesion: 0.24
Nodes (11): step10b_mcp(), main(), _text(), build_mcp_server_config(), expected_mcp_tool_names(), mcp_include_drive(), mcp_subprocess_env(), MCP client configuration — memory + CRM + RAG (+ optional Drive).  Adapted from (+3 more)

### Community 89 - "Test Suite 4"
Cohesion: 0.12
Nodes (15): 10. Known Sandbox Limitations to Flag (be upfront about these, don't get caught off guard), 1. Account Setup (15–30 min), 2. How the Flow Maps to Your Existing Architecture, 3. Install Dependencies, 4. Build the Webhook Endpoint, 5. Critical Constraint: The 3-Second Webhook Window, 6. Exposing Your Local Backend to Twilio (for testing before deployment), 7. Handling Voice Notes (ties into your P0 voice transcription feature) (+7 more)

### Community 90 - "Test Suite 5"
Cohesion: 0.24
Nodes (8): HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required)., FeeCycle, InvoiceStatus, Enum, str, Domain status enums — mirror PostgreSQL ENUM types in sql/01_schema.sql., StaffRole, Domain types — enums and value objects.

### Community 92 - "Design Double Diamond 5"
Cohesion: 0.40
Nodes (5): post, Send a student message and receive an AI reply.      Use this during development, send_chat_message(), ChatRequest, ChatResponse

### Community 93 - "Escalation Routes 8"
Cohesion: 0.21
Nodes (12): _client(), asyncio, _Query, Student channel resolution tests., test_bind_telegram_student_channel_after_enrollment(), test_link_telegram_contact_does_not_link_unenrolled_stub(), test_link_telegram_contact_reuses_enrolled_student(), test_link_telegram_contact_stores_pending_when_unknown_phone() (+4 more)

### Community 94 - "Escalation Routes 9"
Cohesion: 0.18
Nodes (21): Enrollment, Base, Represents a student's enrollment in a subject class., get_dashboard_chat_logs(), get_dashboard_escalations(), get_overview(), get_summary(), get (+13 more)

### Community 96 - "Dashboard Module 4"
Cohesion: 0.53
Nodes (8): _chat(), main(), _phone(), _require_live_env(), scenario_escalation(), scenario_onboarding(), scenario_payment(), scenario_resource_rag()

### Community 97 - "Escalation Routes 11"
Cohesion: 0.31
Nodes (9): add_turn(), get_procedural(), _init(), tool, Memory MCP Server — exposes ST recall / add_turn / procedural lookup.  Adapted f, Fetch recent conversation turns for a tenant session., Append a conversation turn to short-term memory., Lookup tenant onboarding / workflow procedures. (+1 more)

### Community 98 - "Demo Chat Lifecycle 2"
Cohesion: 0.15
Nodes (22): main(), _mock_drive_backend(), Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)., Paper query → Drive link (mock backend; no Google credentials)., Velocity query → cited RAG answer (mocked RAG service)., smoke_drive_paper_link(), smoke_rag_velocity_live(), smoke_rag_velocity_mock() (+14 more)

### Community 99 - "Admissions Onboarding 16"
Cohesion: 0.22
Nodes (8): AGENTS.md — Axiom AI Backend, Environment, Gotchas, Linting, LLM Providers, Project Structure, Quick Commands, Testing

### Community 100 - "Escalation Routes 12"
Cohesion: 0.22
Nodes (9): 11. API Contract Summary (Dashboard Team), 12. Environment Variables, 13. Explicitly Out of MVP Scope, 14. Per-Phase Workflow, 15. Day-by-Day Schedule, 1. Locked Architecture Decisions, Appendix: Generic Template, Axiom AI — AI Backend Roadmap (+1 more)

### Community 101 - "Dashboard Module 5"
Cohesion: 0.22
Nodes (9): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 0 — Foundation & Multi-Tenant Schema, Reference Implementation (copy — do not invent) (+1 more)

### Community 102 - "Test Suite 6"
Cohesion: 0.22
Nodes (9): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 1 — Dev Chat + Messaging Pipeline *(Twilio deferred)*, Reference Implementation (copy — do not invent) (+1 more)

### Community 103 - "Admissions Onboarding 17"
Cohesion: 0.14
Nodes (13): 10. Setup Checklist for Your Two-Tutor Pilot, 1. Why "One Bot Per Tutor/Institute" Is the Right Call, 2. Creating a Bot (per tutor/institute) — 2 Minutes Each, 3. Webhook Architecture — One Endpoint, Tenant Identified by URL Path, 4. Sending Responses Back, 5. Solving Your Core Requirement: Identifying the Student by Phone Number, 6. Data Model Addition (small, additive change to your existing schema), 7. Handling Images (Payment Slips) and Voice Notes — Both Native to Telegram (+5 more)

### Community 104 - "MCP Integration 3"
Cohesion: 0.29
Nodes (4): Open (or return existing) escalation for dashboard inbox., Legacy alias — creates payment_receipt escalation without bank_slip storage., Staff rejects payment — closes escalation without activating enrollment., is_payment_reason()

### Community 105 - "Admissions Onboarding 18"
Cohesion: 0.28
Nodes (8): get_student(), Any, get, post, Student registration and lookup — dashboard + dev API., Register or update a student profile (dashboard / manual onboarding)., Fetch student profile and enrollments by phone., register_student()

### Community 106 - "Escalation Routes 13"
Cohesion: 0.25
Nodes (7): API Key Auth via Header, CORS Configuration, FastAPI OAuth2 Bearer Dependency, Hide OpenAPI Docs by Default, JWT Create/Verify (python-jose), Password Hashing (passlib + bcrypt), Security Patterns

### Community 107 - "Dashboard API Routes 3"
Cohesion: 0.25
Nodes (7): Build, Demo UI — WhatsApp Student Chat, Env (optional), Features, Prerequisites, Project layout, Quick start

### Community 108 - "MCP Integration 4"
Cohesion: 0.20
Nodes (12): handle_text_message(), client(), asyncio, fixture, Telegram webhook + ChatPipeline wiring tests., test_handle_contact_greets_already_enrolled_student(), test_handle_contact_starts_enrollment_for_new_phone(), test_handle_photo_passes_media_url_into_pipeline() (+4 more)

### Community 109 - "RAG Ingest Pipeline 6"
Cohesion: 0.15
Nodes (12): AXIOM AI — Telegram Integration: Implementation Plan for Cursor, Explicit Non-Goals for This Task (tell Cursor not to touch these), Pre-requisites (do these manually before starting, not part of the coding task), Suggested Build Order (for a single session with Cursor), TASK 1 — Database: Add Telegram Channel Support, TASK 2 — Config: Per-Tenant Bot Token Storage & Lookup, TASK 3 — Telegram Client: Send Messages, Fetch Files, TASK 4 — Webhook Endpoint: Receive & Route Telegram Updates (+4 more)

### Community 110 - "Supabase DB Client 5"
Cohesion: 0.25
Nodes (8): 9.1 Usability and Accessibility, 9.2 Performance and Scalability, 9.3 Reliability and Availability, 9.4 Security, 9.5 Data Privacy and Regulatory Compliance, 9.6 Messaging and AI Cost Governance (New), 9.7 Maintainability and Observability, 9\. Non-Functional Requirements

### Community 111 - "Test Suite 7"
Cohesion: 0.29
Nodes (7): _count_rows(), dashboard_overview(), Any, DashboardTenant, get, Dashboard overview stats for staff home screen., Aggregate counts for dashboard landing page.

### Community 112 - "Dashboard Module 6"
Cohesion: 0.25
Nodes (14): _dispatch(), Any, _display_name(), _ensure_onboarding_session(), handle_contact_shared(), handle_photo_message(), handle_voice_message(), _largest_photo_file_id() (+6 more)

### Community 113 - "RAG Ingest Pipeline 7"
Cohesion: 0.36
Nodes (7): _init(), kb_ingest_status(), kb_search(), tool, RAG MCP Server — tenant-scoped tutor-note Q&A., Search tutor lesson notes (Qdrant) and return a grounded answer with citations., Return Qdrant ingest status for a tenant's tutor-note collection.

### Community 114 - "Chat Message Pipeline 5"
Cohesion: 0.24
Nodes (17): bind_telegram_student_channel(), _delete_pending(), _has_enrollment(), link_telegram_contact(), _lookup_pending_phone(), _lookup_student_by_phone(), _parse_channel(), _pending_identity() (+9 more)

### Community 115 - "Langfuse Runtime 6"
Cohesion: 0.11
Nodes (11): get, FastAPI application — Phase 6 integration (MCP warmup + dashboard APIs)., root(), BaseHTTPMiddleware, Request, Response, Request ID and latency headers., RequestContextMiddleware (+3 more)

### Community 116 - "Dashboard Module 7"
Cohesion: 0.25
Nodes (5): client(), fixture, patch, PDF ingest upload endpoint tests., test_ingest_upload_pdf()

### Community 117 - "Dashboard Module 8"
Cohesion: 0.29
Nodes (4): db_conn(), _db_url(), fixture, Validate v2 ER schema tables exist in Supabase when DATABASE_URL is configured.

### Community 118 - "Student Chat Deps 6"
Cohesion: 0.32
Nodes (6): OverviewPage(), MetricCard(), MetricCardProps, DashboardOverview, getDashboardOverview(), getDashboardSummary()

### Community 119 - "Demo Chat Lifecycle 3"
Cohesion: 0.32
Nodes (6): mainNavItems, NavItem, settingsNavItem, Sidebar(), SidebarProps, cn()

### Community 120 - "Chat Message Pipeline 6"
Cohesion: 0.29
Nodes (7): 8.1 MCP Tool Architecture (MVP), 8. Reference Patterns to Reuse, Debug / REST parity, `mcp_config.py`, MCP servers (MVP scope), Tenant context, Wiring pattern

### Community 121 - "MCP Integration 5"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Dependencies, Features, Files / Modules, Objective, Phase 2 — Agent Framework (Decision Graph + Chat Pipeline), Reference Implementation (copy — do not invent)

### Community 122 - "verify phase0 py"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Features, Files / Modules, Google Drive MVP Approach, Objective, Phase 4 — Resource Agent (Drive + RAG), Reference Implementation (copy — do not invent)

### Community 123 - "Resource Agent 3"
Cohesion: 0.29
Nodes (6): get_chat_logs(), ChatTurnsResponse, DashboardTenant, get, Dashboard chat history — legacy alias under /chat-logs., Legacy path for conversation history.      Prefer `GET /dashboard/chat/conversat

### Community 124 - "Dashboard Frontend Deps 2"
Cohesion: 0.38
Nodes (6): active_tenant_scope(), client(), client_no_tenant_override(), fixture, Shared pytest bootstrap., # IMPORTANT:

### Community 125 - "Dashboard Module 9"
Cohesion: 0.33
Nodes (4): geistMono, geistSans, metadata, ThemeInitializer()

### Community 126 - "Dashboard Module 10"
Cohesion: 0.33
Nodes (5): Demo script — Student chat only (~5 min), Narrative, Payment approval (outside this UI), Steps, Troubleshooting

### Community 127 - "Dashboard Module 11"
Cohesion: 0.33
Nodes (6): 10. Phased Implementation Plan, Acceptance Criteria, Features, Objective, Phase 6 — Integration, Testing & Handoff, Reference Implementation (copy — do not invent)

### Community 128 - "Dashboard API Routes 4"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features, Files / Modules, Objective, Phase 3 — Admissions Agent, Reference Implementation (copy — do not invent)

### Community 129 - "Student Chat Deps 7"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features *(original plan — see PHASE5_DECISIONS.md for what changed)*, Files / Modules, Objective, Phase 5 — Payment Check, Escalation & Dashboard APIs, Reference Implementation (copy — do not invent)

### Community 130 - "Decision Graph 4"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 131 - "Supabase DB Client 6"
Cohesion: 0.33
Nodes (6): 8.1 Agentic Workforce and Conversational Interface, 8.2 Financial and Ticket Management, 8.3 Administrative Dashboard and Agency CRM, 8.5 Marketing and Lead Management, 8.6 Platform Administration and Multi-Tenancy (New), 8\. Functional Requirements

### Community 132 - "Smoke Scripts"
Cohesion: 0.25
Nodes (4): main(), Send WhatsApp messages via Twilio REST API., Thin wrapper around Twilio Messages API with dry-run support., TwilioMessagingClient

### Community 133 - "preload agent runtime"
Cohesion: 0.33
Nodes (5): list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant.

### Community 134 - "Password Hashing"
Cohesion: 0.33
Nodes (5): list_tenants(), ping_supabase(), Any, Supabase REST client wrapper., Lightweight connectivity check via tenants table.

### Community 135 - "MESSAGING DRY RUN"
Cohesion: 0.36
Nodes (4): AdmissionsAgentResult, _last_user_text(), Any, Admissions agent node — multi-turn onboarding via CRM MCP tools.

### Community 136 - "Dashboard Frontend Deps 3"
Cohesion: 0.40
Nodes (5): asyncio, parametrize, Router intent classification tests., _router_with_content(), test_router_intents()

### Community 137 - "Dashboard Module 12"
Cohesion: 0.24
Nodes (8): ErrorRag, FakeDrive, asyncio, User-facing resource agent reply error sanitization., test_build_resource_drive_reply_hides_internal_error(), test_build_resource_rag_reply_hides_internal_error(), test_kb_search_returns_generic_error_code(), test_resource_agent_rag_path_hides_search_failure()

### Community 138 - "Dashboard Frontend Deps 4"
Cohesion: 0.40
Nodes (5): 2. LLM Model Strategy, Config Files, Merge Points (Gemini), Model Assignments (Locked for MVP), Why Two Models?

### Community 139 - "Dashboard Module 13"
Cohesion: 0.40
Nodes (5): 3. Status Enums & Domain Types, Enum ↔ Langfuse Tags, PostgreSQL ENUM Types (`sql/01_schema.sql`), Python Enums (`src/domain/enums.py`), Rules

### Community 140 - "Dashboard Module 14"
Cohesion: 0.40
Nodes (5): 4. Langfuse Observability & Prompt Management, Environment, Phase Deliverables for Langfuse, Prompt Management — Langfuse as Source of Truth, Tracing — Per Tenant, Session, User

### Community 141 - "Dashboard Module 15"
Cohesion: 0.40
Nodes (5): 5. System Understanding, Agent Roster (MVP — 4 specialists + router), Business Problem, MVP Solution (AI Backend), Success Metrics (from MVP Definition)

### Community 142 - "Dashboard Module 16"
Cohesion: 0.60
Nodes (4): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog()

### Community 143 - "Dashboard Module 17"
Cohesion: 0.20
Nodes (9): post, Request, Telegram Bot API webhook router — one bot (token) per tenant., Receive Telegram updates for a single tenant bot.      Always acknowledges with, telegram_webhook(), ensure_tenant_bot(), is_tenant_bot_error(), BaseException (+1 more)

### Community 144 - "Student Chat Deps 8"
Cohesion: 0.29
Nodes (9): admissions_route_decision(), apply_onboarding_patch_overrides(), is_onboarding_active(), onboarding_router_context_hint(), Route-lock helpers — keep mid-onboarding turns on the admissions agent., True when a clear specialist intent should override active onboarding., True when an in-memory onboarding session is collecting details., Force proceed + admissions when mid-onboarding. Returns True if applied. (+1 more)

### Community 145 - "Demo UI"
Cohesion: 0.51
Nodes (9): _async_client(), _json_response(), asyncio, Telegram Bot API client tests — tenant token isolation., test_download_telegram_file_uses_matching_token(), test_get_telegram_file_path(), test_send_contact_request_includes_keyboard(), test_send_telegram_message_uses_tenant_token() (+1 more)

### Community 146 - "Langfuse Runtime 7"
Cohesion: 0.50
Nodes (4): 7. Multi-Tenant Data Model, Core Entities, Shared Supabase for Dashboard Team, Tenant Resolution (Inbound Twilio)

### Community 147 - "LangGraph Supervisor Orchestrator"
Cohesion: 0.50
Nodes (4): 4.1 User Role Overview, 4.2 Student Profile, 4.3 Tutor and Agency Admin Profile, 4\. Stakeholders and User Roles

### Community 148 - "Sri Lankan Private"
Cohesion: 0.83
Nodes (3): check_live(), main(), run_pytest()

### Community 151 - "Langfuse Runtime 8"
Cohesion: 0.67
Nodes (3): 6. Resource Split: Google Drive vs RAG, Google Drive — Tutes & Textbooks Only, RAG (Qdrant) — Tutor Notes Only

### Community 152 - "Langfuse Runtime 9"
Cohesion: 0.67
Nodes (3): 9. High-Level Architecture, Decision Graph — BookMe-AI Pattern (No CAG/CRAG), Processing Model (No Redis)

### Community 153 - "Dashboard Module 18"
Cohesion: 0.67
Nodes (3): 10.1 Agent Roster, 10.2 Conceptual Data Flow, 10\. System Architecture Overview (High Level)

### Community 154 - "Escalation Routes 14"
Cohesion: 0.67
Nodes (3): 16.1 Constraints, 16.2 Assumptions, 16\. Constraints and Assumptions

### Community 155 - "run py"
Cohesion: 0.67
Nodes (3): 2.1 Purpose, 2.2 In Scope / Out of Scope, 2\. Purpose, Scope, and Definitions

### Community 156 - "llm init py"
Cohesion: 0.67
Nodes (3): 3.1 Adjacent Tools and Why They Fall Short, 3.2 Tutor AI's Differentiation, 3\. Market and Competitive Context

### Community 157 - "src init py"
Cohesion: 0.67
Nodes (3): 7.1 Student and Parent Stories, 7.2 Tutor and Admin Stories (CRM Focused), 7\. User Stories

### Community 158 - "Admissions Onboarding 20"
Cohesion: 0.67
Nodes (3): Axiom AI — Multi-Agent Backend, Docs, Quick start

### Community 178 - "memory init py"
Cohesion: 0.32
Nodes (11): _chain_mock(), patch, Dashboard API HTTP tests (mocked Supabase + CRM)., test_dashboard_chat_conversations(), test_dashboard_chat_logs_alias(), test_dashboard_chat_thread(), test_dashboard_overview(), test_dashboard_staff_send_returns_502_when_delivery_fails() (+3 more)

### Community 214 - "RateLimitMiddleware"
Cohesion: 0.31
Nodes (4): BaseHTTPMiddleware, Request, Response, RateLimitMiddleware

### Community 215 - "tenant_scope.py"
Cohesion: 0.42
Nodes (11): ChatChannel, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, MessageRole, PaymentStatus, Enum (+3 more)

### Community 216 - "validate"
Cohesion: 0.31
Nodes (8): active_config(), health(), get, Request, Health, readiness, and config endpoints., ready(), langfuse_configured(), HealthResponse

### Community 217 - "FakeCrm"
Cohesion: 0.36
Nodes (5): FakeCrm, asyncio, Payment Check agent tests., test_payment_agent_creates_escalation_with_media(), test_payment_agent_requires_media()

### Community 218 - "Phase 5 — Escalations + staff chat"
Cohesion: 0.29
Nodes (7): PaymentStatusUpdate, Example dashboard PATCH body using domain enums., parametrize, test_enum_values(), test_payment_status_update_accepts_enum(), test_payment_status_update_rejects_invalid(), test_tenant_summary_schema()

### Community 220 - "FakeCrm"
Cohesion: 0.33
Nodes (4): FakeCrm, asyncio, Escalation agent tests., test_escalation_agent_creates_talk_to_tutor_ticket()

### Community 221 - "get_default_embeddings"
Cohesion: 0.29
Nodes (7): Dashboard overview & chat logs, Escalations (payment + talk-to-tutor), Flow 1 — Payment receipt → dashboard inbox, Flow 2 — Talk to tutor, Phase 5 — Escalations + staff chat, Staff chat (dashboard integration), Staff reply

### Community 222 - "log.py"
Cohesion: 0.40
Nodes (4): _InterceptHandler, Centralised loguru setup (stderr-only for future MCP safety)., setup_logging(), LogRecord

### Community 223 - "test_run_resource_agent_requires_mcp_clients_when_fallback_disabled"
Cohesion: 0.50
Nodes (3): asyncio, Resource agent — in-process tools blocked when ALLOW_INPROCESS_TOOLS=false., test_run_resource_agent_requires_mcp_clients_when_fallback_disabled()

### Community 225 - "main"
Cohesion: 0.38
Nodes (6): profileToForm(), SettingsFormState, SettingsPage(), getTenantProfile(), TenantProfile, updateTenantProfile()

### Community 226 - "_load_env"
Cohesion: 0.33
Nodes (5): post, Document ingest — PDF upload → parent-child chunk → Qdrant., Upload a tutor PDF, extract text, parent-child chunk, embed, and upsert to Qdran, upload_document(), UploadFile

### Community 229 - ".resolve_escalation"
Cohesion: 0.33
Nodes (3): Reason-aware resolve: payment → activate enrollment; tutor → close only., Staff approves payment — activates pending enrollment., Backward-compatible alias for payment resolve.

### Community 230 - "test_merge_response.py"
Cohesion: 0.50
Nodes (4): asyncio, Merge response node tests., test_merge_multiple_fragments_uses_gemini(), test_merge_single_fragment_passthrough()

### Community 231 - "document_from_pdf"
Cohesion: 0.40
Nodes (5): document_from_pdf(), extract_pdf_text(), PDF text extraction for tutor document uploads., Extract plain text from a PDF byte stream., Build ingest document dict from uploaded PDF bytes.

### Community 232 - "8. Implementation phases"
Cohesion: 0.40
Nodes (5): 8. Implementation phases, Phase A — Scaffold (~2h), Phase B — Student lifecycle (~2h), Phase C — Staff console (~2h), Phase D — Polish & docs (~1h)

### Community 233 - "test_routing_smoke.py"
Cohesion: 0.60
Nodes (4): main(), _primary_route(), RoutingCase, _run()

## Knowledge Gaps
- **599 isolated node(s):** `name`, `private`, `version`, `type`, `description` (+594 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IdentityContext` connect `Test Suite 3` to `Chat Message Pipeline`, `Smoke Scripts`, `Chat Message Pipeline 2`, `Chat Message Pipeline 3`, `Langfuse Runtime 2`, `Escalation Routes 6`, `Drive Tooling 4`, `Dashboard API Routes 2`, `Agent Orchestrator`, `Drive Tooling 3`, `Admissions Onboarding 9`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `CrmTool` connect `Decision Graph` to `Demo Chat Lifecycle`, `.resolve_escalation`, `MCP Integration 3`, `Admissions Onboarding 18`, `Admissions Onboarding 6`, `Drive Tooling`, `Workshop Exploration`, `Langfuse Runtime 3`, `._assert_tenant`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `DriveTool` connect `Admissions Onboarding 7` to `Demo Chat Lifecycle 2`, `MCP Integration`, `Memory MCP Path`, `Resource Agent 2`, `Student Chat Deps 4`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 56 inferred relationships involving `get_supabase_client()` (e.g. with `main()` and `step6_tenant()`) actually correct?**
  _`get_supabase_client()` has 56 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `OnboardingFlow` (e.g. with `main()` and `AdmissionsAgent`) actually correct?**
  _`OnboardingFlow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `AgentState` (e.g. with `AdmissionsAgent` and `AdmissionsAgentResult`) actually correct?**
  _`AgentState` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `IdentityContext` (e.g. with `main()` and `main()`) actually correct?**
  _`IdentityContext` has 17 INFERRED edges - model-reasoned connections that need verification._