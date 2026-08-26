# Graph Report - Axiom-AI  (2026-08-26)

## Corpus Check
- 336 files · ~467,536 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3044 nodes · 5747 edges · 218 communities (185 shown, 33 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 978 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3d8ca1bb`
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
- ShortTermMemoryStore
- Dashboard Module 2
- Admissions Onboarding 13
- infrastructure config py
- Langfuse Runtime 5
- Admissions Onboarding 14
- test_identity_recall.py
- _tracing_enabled
- Escalation Routes 6
- Escalation Routes 7
- Drive Tooling 4
- Resource Agent 2
- Dashboard Module 3
- Dashboard API Routes 2
- MCP Integration 2
- Test Suite 4
- Test Suite 5
- TwilioMessagingClient
- Escalation Routes 8
- test_twilio_webhook.py
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
- escalation_reasons.py
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
- P0 — Must finalize (MVP gate)
- preload agent runtime
- page_needs_ocr
- test_run_resource_agent_requires_mcp_clients_when_fallback_disabled
- Dashboard Frontend Deps 3
- Dashboard Frontend Deps 4
- Dashboard Module 13
- Dashboard Module 14
- Dashboard Module 15
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
- FakeCrm
- ._assert_tenant
- FakeCrm
- log.py
- register_telegram_webhook.py
- main
- .resolve_escalation

## God Nodes (most connected - your core abstractions)
1. `get_supabase_client()` - 57 edges
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

## Communities (218 total, 33 thin omitted)

### Community 0 - "Admissions Onboarding"
Cohesion: 0.07
Nodes (25): main(), _format_lkr_amount(), OnboardingFlow, OnboardingSlots, Any, Multi-turn admissions onboarding — slot tracking and class disambiguation., Determine onboarding progress and extract slots from user messages., Onboarding flow unit tests. (+17 more)

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
Cohesion: 0.05
Nodes (51): main(), build_orchestrator(), In-process MemoryTool path (dev/tests without MCP subprocesses)., get_api_key(), _get_bool(), get_chat_model(), get_embedding_model(), _get_nested() (+43 more)

### Community 6 - "Dashboard Frontend Pages"
Cohesion: 0.07
Nodes (39): ClassFormState, emptyForm, ApiError, approvePayment(), assignEscalation(), ChatSender, ChatTurn, ClassDocumentUploadResponse (+31 more)

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
Cohesion: 0.12
Nodes (19): AgentOrchestrator, AgentResponse, _emit_from_config(), _format_session_memory(), _invoke_llm_text(), _last_user_text(), _llm_content_to_str(), _mcp_result_to_str() (+11 more)

### Community 13 - "Design Double Diamond"
Cohesion: 0.12
Nodes (17): Axiom AI Backend — Finalize Checklist, Demo UI (`demo-ui-org/`), Documentation sync, Enable Drive MCP in runtime, How to use, P1 — Demo polish, P2 — Google Drive MCP integration, Per-tenant onboarding (+9 more)

### Community 14 - "Design Double Diamond 2"
Cohesion: 0.14
Nodes (21): AuthContext, AuthContextValue, AuthProvider(), request(), AuthApiError, authRequest(), getMe(), loginStaff() (+13 more)

### Community 15 - "Admissions Onboarding 5"
Cohesion: 0.06
Nodes (71): get_drive_tool(), get_rag_tool(), get_request_id(), Request, FastAPI dependency injection helpers., _require_startup(), active_config(), health() (+63 more)

### Community 16 - "Dashboard Frontend Deps"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "Admissions Onboarding 6"
Cohesion: 0.12
Nodes (29): commit_onboarding(), create_enrollment(), create_escalation(), get_class_details(), get_student(), get_tenant_info(), _init(), list_classes() (+21 more)

### Community 18 - "Drive Tooling"
Cohesion: 0.06
Nodes (28): Memory business logic — called by MCP server only (Week 13 pattern)., _count_rows(), dashboard_overview(), Any, DashboardTenant, get, Dashboard overview stats for staff home screen., Aggregate counts for dashboard landing page. (+20 more)

### Community 19 - "API Chat Schemas"
Cohesion: 0.13
Nodes (14): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory(), _mcp_text(), McpDriveClient, McpRagClient (+6 more)

### Community 20 - "Design Double Diamond 3"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+16 more)

### Community 21 - "Decision Graph"
Cohesion: 0.16
Nodes (12): CrmTool, mock_db(), fixture, CRM tool and tenant isolation tests., test_commit_onboarding_completes_unenrolled_profile(), test_commit_onboarding_rejects_already_enrolled(), test_create_enrollment_rejects_cross_tenant_class(), test_create_enrollment_requires_consent() (+4 more)

### Community 22 - "Dashboard ORM Models"
Cohesion: 0.06
Nodes (27): AuditLog, Base, Records all staff actions performed within the system., BankSlipUpload, Base, Represents a bank slip uploaded by a student for invoice verification., Escalation, Base (+19 more)

### Community 23 - "Admissions Onboarding 7"
Cohesion: 0.05
Nodes (45): main(), smoke_drive_mock(), smoke_ingest_load(), smoke_resource_agent(), DriveTool, _normalize_drive_folder_id(), Any, Drive tool — tenant-scoped paper/textbook/syllabus search. (+37 more)

### Community 24 - "Agent Orchestrator"
Cohesion: 0.11
Nodes (21): main(), main(), Send a student message and receive an AI reply.      Use this during development, send_chat_message(), ChatPipeline, Channel-agnostic chat pipeline — HTTP dev chat + Twilio webhook., Sync entry for scripts and tests without a running event loop., ChatTurnResult (+13 more)

### Community 25 - "Admissions Onboarding 8"
Cohesion: 0.08
Nodes (25): API Design, Async Routes, Async Test Client from Day 0, Chain Dependencies, CPU Intensive Tasks, Custom Base Model, Decouple BaseSettings, Dependencies (+17 more)

### Community 26 - "Drive Tooling 2"
Cohesion: 0.09
Nodes (27): _breadcrumb(), _contextualize(), fixed_chunk(), _page_of(), parent_child_chunk(), Any, Text chunking strategies — fixed + parent-child, markdown structure aware.  Pare, Split markdown into (breadcrumb, text) sections on headings.      Falls back to (+19 more)

### Community 27 - "Supabase DB Client"
Cohesion: 0.08
Nodes (23): Basic Setup, Batch Messages, Best Practices, FastAPI Caching, FastAPI Rate Limiting, FastAPI Session Management, Hash Operations, Key Expiration (TTL) (+15 more)

### Community 28 - "Agent Orchestrator 2"
Cohesion: 0.08
Nodes (24): 1. Google Cloud, 2. Environment, Architecture, Folder ID, Folder layout, Google Drive MCP — Integration & Testing, Multi-tenant isolation, MVP vs v2 (+16 more)

### Community 29 - "Drive Tooling 3"
Cohesion: 0.09
Nodes (22): 10. Deferred to Phase 3+, 1. Where we are today, 2. Binding constraint: no torch in the runtime image, 3. Target architecture, 4. Chunking upgrade, 5. Phase 1 — extraction router, 6. Phase 2 — correctness and lifecycle, 7. Configuration (+14 more)

### Community 30 - "Identity Context"
Cohesion: 0.09
Nodes (22): Alembic Migration Naming, Async Engine + Session, Bulk Insert, Bulk Operations, Bulk Update, Cascade Delete, Commit/Rollback Pattern, Constraint Naming (+14 more)

### Community 31 - "Admissions Onboarding 9"
Cohesion: 0.11
Nodes (24): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, _routes_from_patch(), run_chat_turn(), classify_confirmation() (+16 more)

### Community 32 - "Admissions Onboarding 10"
Cohesion: 0.15
Nodes (11): _looks_like_text(), SourceType, Detect upload format from content, not from the filename.  Both the filename and, Heuristic: decodable as UTF-8 and free of NUL bytes., Return the source type for ``content``, or raise ExtractionError.      ``filenam, sniff_format(), _zip_format(), _ooxml() (+3 more)

### Community 33 - "Resource Agent"
Cohesion: 0.13
Nodes (16): DashboardLayoutProps, ProtectedDashboard(), Header(), HeaderProps, ToastContainer(), toastStyles(), useAuth(), TenantContext (+8 more)

### Community 34 - "Chat Message Pipeline"
Cohesion: 0.18
Nodes (14): get_tenant_id(), approve_payment(), get_pending_payments(), get, put, Session, reject_payment(), get_tenant_profile() (+6 more)

### Community 35 - "Invoice DB Layer"
Cohesion: 0.12
Nodes (14): preload_agent_runtime(), Any, Store warmed instances from FastAPI lifespan (BookMe AI ``main.py`` pattern)., lifespan(), get, FastAPI application — Phase 6 integration (MCP warmup + dashboard APIs)., Warm agent stack before accepting traffic (BookMe AI ``api/main.py`` pattern)., root() (+6 more)

### Community 36 - "Design Double Diamond 4"
Cohesion: 0.12
Nodes (25): InboxContent(), isPaymentReason(), statusClass(), MessagesContent(), senderBubbleClass(), EscalationSocketEvent, EscalationSocketEventType, useEscalationSocket() (+17 more)

### Community 37 - "RAG Ingest Pipeline 5"
Cohesion: 0.14
Nodes (13): Any, RagTool, RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)., Business logic for kb_search — used by rag_server and debug REST., RAG MCP server — tool surface (same logic as axiom-rag stdio server)., test_rag_mcp_kb_ingest_status(), test_rag_mcp_kb_search_empty_collection(), test_rag_mcp_kb_search_with_citations() (+5 more)

### Community 38 - "Escalation Routes"
Cohesion: 0.40
Nodes (12): assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get_tenant_escalation_or_404(), Escalation, get, put (+4 more)

### Community 39 - "Chat Message Pipeline 2"
Cohesion: 0.18
Nodes (17): classify_info_inquiry(), extract_class_filters(), format_class_details(), _format_lkr_amount(), _format_single_class(), format_staff_list(), format_tenant_info(), looks_like_institute_info() (+9 more)

### Community 40 - "Invoice DB Layer 2"
Cohesion: 0.20
Nodes (37): ChatChannel, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, Enum, str, Domain status enums — mirror PostgreSQL ENUM types in sql/01_schema.sql. (+29 more)

### Community 41 - "Chat Message Pipeline 3"
Cohesion: 0.25
Nodes (12): main(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., Close MCP subprocess client on app shutdown (Week 13 / BookMe pattern)., reset_agent_runtime(), shutdown_agent_runtime() (+4 more)

### Community 42 - "Dashboard ORM Models 2"
Cohesion: 0.07
Nodes (50): client(), _ingest_result(), _minimal_docx(), _post(), fixture, patch, Multi-format ingest upload endpoint tests., OLE2 compound files (.doc) get an actionable message, not a generic 422. (+42 more)

### Community 43 - "Decision Graph 2"
Cohesion: 0.18
Nodes (20): _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_chat_turns(), get_conversation_thread(), get_thread_alias(), list_conversations(), Any (+12 more)

### Community 44 - "Escalation Routes 2"
Cohesion: 0.11
Nodes (19): Architecture, Dashboard overview & chat logs, Dev Chat — WhatsApp Simulator (No Twilio Required), Endpoints, Escalations (payment + talk-to-tutor), Fetch conversation history, Flow 1 — Payment receipt → dashboard inbox, Flow 2 — Talk to tutor (+11 more)

### Community 45 - "Dashboard Module"
Cohesion: 0.25
Nodes (3): client(), fixture, Phase 0 health endpoint tests.

### Community 46 - "Invoice DB Layer 3"
Cohesion: 0.09
Nodes (22): 10. Technical decisions, 11. Risks & mitigations, 12. Acceptance criteria, 13. Future (post-hackathon), 1. Product concept, 2. Folder structure, 3. BookMe AI → Axiom file mapping, 4. API integration (student chat) (+14 more)

### Community 47 - "CRM MCP Server"
Cohesion: 0.18
Nodes (17): build_direct_system_prompt(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply(), build_resource_drive_reply(), build_resource_rag_reply(), build_router_prompt() (+9 more)

### Community 48 - "Escalation Routes 3"
Cohesion: 0.15
Nodes (20): ClassesPage(), IngestContent(), emptyForm, matchesStudentSearch(), ModalMode, StudentsPage(), EnrollModal(), EnrollModalProps (+12 more)

### Community 49 - "Langfuse Runtime"
Cohesion: 0.08
Nodes (25): Dashboard API Contract (Phase 5), Document ingest (knowledge base), Endpoint map, Escalation inbox (unified HITL queue), Escalation object, Get thread (message panel), How to pass tenant, Integration flow (recommended) (+17 more)

### Community 50 - "Langfuse Runtime 2"
Cohesion: 0.15
Nodes (15): main(), main(), _one_turn(), main(), get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session. (+7 more)

### Community 51 - "Test Suite"
Cohesion: 0.09
Nodes (26): _chain_mock(), main(), assert_body_tenant(), Tenant scope validation for staff / dashboard endpoints., Resolved, active tenant — all dashboard queries must use this scope., Resolve tenant from query param or X-Tenant-ID header.      Dashboard frontend s, Ensure the tenant exists and is active before any dashboard handler runs., Reject POST bodies whose tenant_id does not match the resolved scope. (+18 more)

### Community 52 - "Agent Orchestrator 3"
Cohesion: 0.12
Nodes (16): Acceptance criteria mapping, Explicitly out of scope (stay V2), Handoff checklist (dashboard team), Makefile targets (to add), Phase 6 — Implementation Plan, Risk register, Starting point (what’s already done), Suggested schedule (1 day) (+8 more)

### Community 53 - "Admissions Onboarding 11"
Cohesion: 0.11
Nodes (23): _fallback_multi(), heuristic_route(), MultiRouteDecision, _normalize_action(), _pattern_score(), Any, QueryRouter, Query Router — LLM intent classification for tuition agents.  Ported from BookMe (+15 more)

### Community 54 - "Workshop Exploration"
Cohesion: 0.23
Nodes (15): _enrich_escalations(), EscalationActionResponse, list_escalations(), notify_student(), Any, BaseModel, DashboardTenant, get (+7 more)

### Community 55 - "Admissions Onboarding 12"
Cohesion: 0.31
Nodes (6): ErrorRag, FakeDrive, asyncio, User-facing resource agent reply error sanitization., test_kb_search_returns_generic_error_code(), test_resource_agent_rag_path_hides_search_failure()

### Community 56 - "Supabase DB Client 2"
Cohesion: 0.13
Nodes (15): 10. Troubleshooting, 1. Prerequisites, 2. Clone and virtualenv, 3. Environment (`.env`), 4. Database, 5. Langfuse prompts, 6. RAG ingest (optional), 7. Run the API (+7 more)

### Community 57 - "Langfuse Runtime 3"
Cohesion: 0.22
Nodes (8): mock_db(), fixture, CRM escalation create/resolve tests for Phase 5 flows., test_create_payment_escalation(), test_create_talk_to_tutor_escalation(), test_reject_payment_escalation(), test_resolve_payment_escalation_activates_enrollment(), test_resolve_talk_to_tutor_does_not_activate_enrollment()

### Community 58 - "Decision Graph 3"
Cohesion: 0.16
Nodes (22): clear_bot_token_cache(), _fetch_tenant_bot_row(), get_bot_token_for_tenant(), Any, ValueError, Per-tenant Telegram bot token lookup (SRS NFR-17 — not env vars)., Raised when a tenant has no usable Telegram bot token., Drop cached tokens — used by tests and after rotating a token. (+14 more)

### Community 59 - "Test Suite 2"
Cohesion: 0.13
Nodes (21): main(), _primary_route(), RoutingCase, _run(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, build_decision_input(), decide_node() (+13 more)

### Community 60 - "Student Chat Deps 4"
Cohesion: 0.23
Nodes (12): ExtractedDoc, Normalized extraction result handed to the ingest pipeline., _fake_ingest_result(), patch, Ingest pipeline unit tests., The old name is kept for one release; callers should move to run_upload_ingest., test_fixed_chunk_produces_chunks(), test_ingest_documents_parent_child() (+4 more)

### Community 61 - "Workshop Exploration 2"
Cohesion: 0.11
Nodes (27): _mask_path(), step1_environment(), main(), title_from_filename(), _build_parent_lookup(), embed_texts(), _enrich_children_with_parent_text(), ingest_documents() (+19 more)

### Community 62 - "RAG Tooling"
Cohesion: 0.14
Nodes (13): Async Routes, Core Principles, Dependency Injection, Project Structure, Pydantic Validation, python-backend, Quick Patterns, Rate Limiting (+5 more)

### Community 63 - "CRM MCP Server 2"
Cohesion: 0.16
Nodes (21): Enrollment, Base, Represents a student's enrollment in a subject class., get_dashboard_chat_logs(), get_dashboard_escalations(), get_overview(), get_summary(), get (+13 more)

### Community 64 - "Student Chat Deps 5"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, moduleResolution, noEmit, skipLibCheck, strict, target (+3 more)

### Community 65 - "Test Suite 3"
Cohesion: 0.11
Nodes (23): IdentityContext, Resolved tenant + student scope for one WhatsApp conversation., Resolved tenant scope; student_id is set only when a DB record exists., Stable recall key — student id when enrolled, otherwise phone., Past papers and RAG require pending or active enrollment., build_recall_context(), format_student_profile(), Build recall context (student profile + ST turns) before the decision graph. (+15 more)

### Community 66 - "IdentityResolver"
Cohesion: 0.15
Nodes (16): _parse_form_params(), Request, Response, Twilio WhatsApp webhook router., Twilio WhatsApp sandbox webhook.      Returns 200 immediately and processes the, _should_validate_signature(), twilio_webhook(), _webhook_public_url() (+8 more)

### Community 67 - "Chat Message Pipeline 4"
Cohesion: 0.17
Nodes (7): OnboardingState, Hydrate state for an existing database student (post-enrollment paths only)., OnboardingSession, OnboardingSessionStore, In-memory onboarding session store — Week 13 SessionStore pattern.  Onboarding s, Ephemeral multi-turn onboarding progress for one tenant+phone pair., Process-local store keyed by ``tenant_id:phone``.

### Community 68 - "Chat Turn Runner"
Cohesion: 0.19
Nodes (17): Base, Represents a student registered under a tenant., Student, create_student(), delete_student(), enroll_student(), get_student(), get_student_by_phone() (+9 more)

### Community 69 - "Langfuse Runtime 4"
Cohesion: 0.14
Nodes (16): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog(), Propagate tenant/session/user identifiers to all nested Langfuse observations., Langfuse trace scope for a WhatsApp conversation turn., Test helper — clear cached Langfuse client state., reset_langfuse_state() (+8 more)

### Community 70 - "MCP Integration"
Cohesion: 0.18
Nodes (15): PageText, One page of a paginated source document., ocr_available(), Vision transcription of scanned PDF pages via the `ocr` LLM role (Gemini).  Only, Transcribe a small PDF (the starved pages only) to markdown.      Raises Runtime, transcribe_pdf_pages(), _assemble(), extract_pdf() (+7 more)

### Community 71 - "Dashboard API Routes"
Cohesion: 0.18
Nodes (14): Base, Represents a tuition class offered by a tenant., SubjectClass, create_class(), delete_class(), get_class(), get_classes(), _parse_fee_cycle() (+6 more)

### Community 72 - "Escalation Routes 4"
Cohesion: 0.20
Nodes (18): assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get_tenant_escalation_or_404(), Escalation, get, put (+10 more)

### Community 73 - "Memory MCP Path"
Cohesion: 0.29
Nodes (12): _list_children(), main(), _print_summary(), TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).  Does not, step12_network(), step2_auth(), step3_drive_client_direct(), step5_and_10_drive_tool() (+4 more)

### Community 74 - "ShortTermMemoryStore"
Cohesion: 0.36
Nodes (5): FakeCrm, asyncio, Payment Check agent tests., test_payment_agent_creates_escalation_with_media(), test_payment_agent_requires_media()

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
Cohesion: 0.15
Nodes (22): download_telegram_file(), get_telegram_file_path(), _keep_telegram_typing(), Any, Response, _raise_telegram_error(), Thin Telegram Bot API client — one token per tenant, never a global token., Send a message with a one-time 'Share phone number' keyboard. (+14 more)

### Community 79 - "Admissions Onboarding 14"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 80 - "test_identity_recall.py"
Cohesion: 0.27
Nodes (6): IdentityResolver, Any, Lookup tenant by sandbox number and student by sender phone., Resolve identity for HTTP dev chat when tenant_id is known., test_identity_resolver_keeps_enrolled_student(), test_identity_resolver_treats_unenrolled_row_as_visitor()

### Community 81 - "_tracing_enabled"
Cohesion: 0.19
Nodes (15): _disable_langfuse(), get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), prefetch_prompts(), BaseException, Validate API keys once at startup; avoids repeated 401 noise from prompt fetch. (+7 more)

### Community 82 - "Escalation Routes 6"
Cohesion: 0.18
Nodes (7): chat_result(), client(), asyncio, fixture, HTTP dev chat endpoint tests., Regression: /chat must not call asyncio.run() inside FastAPI's event loop., test_chat_pipeline_runs_agent_inside_event_loop()

### Community 83 - "Escalation Routes 7"
Cohesion: 0.22
Nodes (11): FakeDrive, Any, asyncio, patch, Class-scoped RAG retrieval tests., test_kb_search_forwards_class_ids_to_rag_service(), test_resource_agent_blocks_enrolled_without_class_ids(), test_resource_agent_passes_enrolled_class_ids_to_rag() (+3 more)

### Community 84 - "Drive Tooling 4"
Cohesion: 0.10
Nodes (26): build_decision_graph(), _emit_from_config(), make_guardrail_node(), make_router_node(), EmitFn, RunnableConfig, Decision LangGraph — guardrail and router subgraph for Axiom AI.  Ported from Bo, _build_user_prompt() (+18 more)

### Community 85 - "Resource Agent 2"
Cohesion: 0.17
Nodes (11): classify_resource_subpath(), _infer_drive_folder(), _last_user_text(), Keyword sub-router: drive for file requests, rag for explanations., ResourceAgentResult, get_resource_not_enrolled_reply(), parametrize, Resource agent sub-router tests. (+3 more)

### Community 86 - "Dashboard Module 3"
Cohesion: 0.16
Nodes (10): ExtractionError, normalize_markdown(), ValueError, Shared types for document extraction.  Every extractor converts source bytes int, Clean up extractor output so headings are usable as breadcrumbs.      Layout-der, Raised when a document cannot be turned into usable markdown.      Subclasses Va, extract_markdown(), Markdown / plain-text passthrough. (+2 more)

### Community 87 - "Dashboard API Routes 2"
Cohesion: 0.25
Nodes (8): Agent pipeline, Bot & environment, Documentation, Identity & persistence, Inbound webhook, Outbound messaging, P2 — Telegram Bot integration, Testing

### Community 88 - "MCP Integration 2"
Cohesion: 0.24
Nodes (6): MessagePersistence, ChatChannel, MessageRole, Persist inbound/outbound messaging to Supabase (message_logs + st_turns)., Write message_logs and st_turns rows for a conversation turn., Persist a staff-authored message (role=system → sender=staff in dashboard UI).

### Community 89 - "Test Suite 4"
Cohesion: 0.12
Nodes (15): 10. Known Sandbox Limitations to Flag (be upfront about these, don't get caught off guard), 1. Account Setup (15–30 min), 2. How the Flow Maps to Your Existing Architecture, 3. Install Dependencies, 4. Build the Webhook Endpoint, 5. Critical Constraint: The 3-Second Webhook Window, 6. Exposing Your Local Backend to Twilio (for testing before deployment), 7. Handling Voice Notes (ties into your P0 voice transcription feature) (+7 more)

### Community 90 - "Test Suite 5"
Cohesion: 0.24
Nodes (11): step10b_mcp(), main(), _text(), build_mcp_server_config(), expected_mcp_tool_names(), mcp_include_drive(), mcp_subprocess_env(), MCP client configuration — memory + CRM + RAG (+ optional Drive).  Adapted from (+3 more)

### Community 92 - "TwilioMessagingClient"
Cohesion: 0.23
Nodes (8): extract_docx(), _heading_level(), _looks_like_heading(), _promote_bold_headings(), DOCX → markdown via mammoth (HTML) → markdownify.  mammoth keys off Word's *sema, Turn standalone whole-line bold paragraphs into markdown headings., Extract markdown from .docx bytes., TestPromoteBoldHeadings

### Community 93 - "Escalation Routes 8"
Cohesion: 0.07
Nodes (43): Supabase access for admissions CRM operations., bind_telegram_student_channel(), _delete_pending(), _has_enrollment(), link_telegram_contact(), _lookup_pending_phone(), _lookup_student_by_phone(), _parse_channel() (+35 more)

### Community 94 - "test_twilio_webhook.py"
Cohesion: 0.18
Nodes (7): parse_twilio_form(), Parse Twilio application/x-www-form-urlencoded webhook bodies., client(), identity_ctx(), fixture, Twilio webhook endpoint tests., test_parse_twilio_form_extracts_media()

### Community 96 - "Dashboard Module 4"
Cohesion: 0.47
Nodes (9): _chat(), main(), _phone(), _require_live_env(), scenario_escalation(), scenario_onboarding(), scenario_out_of_scope(), scenario_payment() (+1 more)

### Community 97 - "Escalation Routes 11"
Cohesion: 0.31
Nodes (9): add_turn(), get_procedural(), _init(), tool, Memory MCP Server — exposes ST recall / add_turn / procedural lookup.  Adapted f, Fetch recent conversation turns for a tenant session., Append a conversation turn to short-term memory., Lookup tenant onboarding / workflow procedures. (+1 more)

### Community 98 - "Demo Chat Lifecycle 2"
Cohesion: 0.12
Nodes (26): main(), _mock_drive_backend(), Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)., Paper query → Drive link (mock backend; no Google credentials)., Velocity query → cited RAG answer (mocked RAG service)., smoke_drive_paper_link(), smoke_rag_velocity_live(), smoke_rag_velocity_mock() (+18 more)

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
Cohesion: 0.42
Nodes (11): ChatChannel, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, MessageRole, PaymentStatus, Enum (+3 more)

### Community 105 - "Admissions Onboarding 18"
Cohesion: 0.32
Nodes (7): get_student(), Any, get, Student registration and lookup — dashboard + dev API., Register or update a student profile (dashboard / manual onboarding)., Fetch student profile and enrollments by phone., register_student()

### Community 106 - "Escalation Routes 13"
Cohesion: 0.25
Nodes (7): API Key Auth via Header, CORS Configuration, FastAPI OAuth2 Bearer Dependency, Hide OpenAPI Docs by Default, JWT Create/Verify (python-jose), Password Hashing (passlib + bcrypt), Security Patterns

### Community 107 - "Dashboard API Routes 3"
Cohesion: 0.25
Nodes (7): Build, Demo UI — WhatsApp Student Chat, Env (optional), Features, Prerequisites, Project layout, Quick start

### Community 108 - "MCP Integration 4"
Cohesion: 0.17
Nodes (21): handle_text_message(), client(), _noop_typing(), asyncio, fixture, Telegram webhook + ChatPipeline wiring tests., skip_typing(), test_handle_contact_greets_already_enrolled_student() (+13 more)

### Community 109 - "RAG Ingest Pipeline 6"
Cohesion: 0.15
Nodes (12): AXIOM AI — Telegram Integration: Implementation Plan for Cursor, Explicit Non-Goals for This Task (tell Cursor not to touch these), Pre-requisites (do these manually before starting, not part of the coding task), Suggested Build Order (for a single session with Cursor), TASK 1 — Database: Add Telegram Channel Support, TASK 2 — Config: Per-Tenant Bot Token Storage & Lookup, TASK 3 — Telegram Client: Send Messages, Fetch Files, TASK 4 — Webhook Endpoint: Receive & Route Telegram Updates (+4 more)

### Community 110 - "Supabase DB Client 5"
Cohesion: 0.25
Nodes (8): 9.1 Usability and Accessibility, 9.2 Performance and Scalability, 9.3 Reliability and Availability, 9.4 Security, 9.5 Data Privacy and Regulatory Compliance, 9.6 Messaging and AI Cost Governance (New), 9.7 Maintainability and Observability, 9\. Non-Functional Requirements

### Community 111 - "Test Suite 7"
Cohesion: 0.35
Nodes (5): AdmissionsAgentResult, _last_user_text(), Any, Admissions agent node — multi-turn onboarding via CRM MCP tools., run_admissions_agent()

### Community 112 - "Dashboard Module 6"
Cohesion: 0.14
Nodes (20): _dispatch(), Any, Request, Telegram Bot API webhook router — one bot (token) per tenant., Receive Telegram updates for a single tenant bot.      Always acknowledges with, telegram_webhook(), _display_name(), _ensure_onboarding_session() (+12 more)

### Community 113 - "RAG Ingest Pipeline 7"
Cohesion: 0.36
Nodes (7): _init(), kb_ingest_status(), kb_search(), tool, RAG MCP Server — tenant-scoped tutor-note Q&A., Search tutor lesson notes (Qdrant) and return a grounded answer with citations., Return Qdrant ingest status for a tenant's tutor-note collection.

### Community 114 - "escalation_reasons.py"
Cohesion: 0.18
Nodes (6): CRM business logic — called by MCP server only (Week 13 pattern)., Open (or return existing) escalation for dashboard inbox., Legacy alias — creates payment_receipt escalation without bank_slip storage., Staff rejects payment — closes escalation without activating enrollment., is_payment_reason(), Escalation reason codes for dashboard inbox filtering.

### Community 115 - "Langfuse Runtime 6"
Cohesion: 0.29
Nodes (5): BaseHTTPMiddleware, Request, Response, Request ID and latency headers., RequestContextMiddleware

### Community 116 - "Dashboard Module 7"
Cohesion: 0.29
Nodes (9): admissions_route_decision(), apply_onboarding_patch_overrides(), is_onboarding_active(), onboarding_router_context_hint(), Route-lock helpers — keep mid-onboarding turns on the admissions agent., True when a clear specialist intent should override active onboarding., True when an in-memory onboarding session is collecting details., Force proceed + admissions when mid-onboarding. Returns True if applied. (+1 more)

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
Cohesion: 0.27
Nodes (6): extract_document(), max_upload_bytes(), SourceType, Multi-format document extraction — PDF, DOCX and Markdown to markdown.  Every ex, Sniff the format of ``content`` and extract it to markdown.      Raises Extracti, TestExtractDocument

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

### Community 132 - "P0 — Must finalize (MVP gate)"
Cohesion: 0.25
Nodes (8): Core agent & routing, Dashboard handoff, Error handling (Phase 6 WS5), Langfuse, Live infrastructure, P0 — Must finalize (MVP gate), Phase 6 E2E scripts, RAG (tutor notes)

### Community 133 - "preload agent runtime"
Cohesion: 0.33
Nodes (5): list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant.

### Community 134 - "page_needs_ocr"
Cohesion: 0.43
Nodes (3): page_needs_ocr(), True when a page's text layer yielded too little to be real content.      Catche, TestPageNeedsOcr

### Community 135 - "test_run_resource_agent_requires_mcp_clients_when_fallback_disabled"
Cohesion: 0.50
Nodes (3): asyncio, Resource agent — in-process tools blocked when ALLOW_INPROCESS_TOOLS=false., test_run_resource_agent_requires_mcp_clients_when_fallback_disabled()

### Community 136 - "Dashboard Frontend Deps 3"
Cohesion: 0.40
Nodes (5): asyncio, parametrize, Router intent classification tests., _router_with_content(), test_router_intents()

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

### Community 145 - "Demo UI"
Cohesion: 0.44
Nodes (12): _async_client(), _json_response(), asyncio, Telegram Bot API client tests — tenant token isolation., test_download_telegram_file_uses_matching_token(), test_get_telegram_file_path(), test_send_contact_request_includes_keyboard(), test_send_telegram_chat_action_does_not_raise() (+4 more)

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

### Community 214 - "RateLimitMiddleware"
Cohesion: 0.36
Nodes (4): BaseHTTPMiddleware, Request, Response, RateLimitMiddleware

### Community 215 - "tenant_scope.py"
Cohesion: 0.15
Nodes (13): get_db(), MessageLog, Base, Stores metadata about conversations between students and the AI assistant., create_message_log(), get_message_logs(), get, Session (+5 more)

### Community 217 - "FakeCrm"
Cohesion: 0.16
Nodes (14): EscalationAgentResult, _last_user_text(), Escalation agent — talk-to-tutor requests → dashboard inbox., run_escalation_agent(), _last_user_text(), PaymentAgent, PaymentAgentResult, Payment Check agent — payment receipt → escalation inbox. (+6 more)

### Community 220 - "FakeCrm"
Cohesion: 0.33
Nodes (4): FakeCrm, asyncio, Escalation agent tests., test_escalation_agent_creates_talk_to_tutor_ticket()

### Community 222 - "log.py"
Cohesion: 0.40
Nodes (4): _InterceptHandler, Centralised loguru setup (stderr-only for future MCP safety)., setup_logging(), LogRecord

### Community 225 - "main"
Cohesion: 0.38
Nodes (6): profileToForm(), SettingsFormState, SettingsPage(), getTenantProfile(), TenantProfile, updateTenantProfile()

### Community 229 - ".resolve_escalation"
Cohesion: 0.33
Nodes (3): Reason-aware resolve: payment → activate enrollment; tutor → close only., Staff approves payment — activates pending enrollment., Backward-compatible alias for payment resolve.

## Knowledge Gaps
- **617 isolated node(s):** `name`, `private`, `version`, `type`, `description` (+612 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CrmTool` connect `Decision Graph` to `Demo Chat Lifecycle`, `.resolve_escalation`, `Admissions Onboarding 18`, `Admissions Onboarding 6`, `Drive Tooling`, `escalation_reasons.py`, `Workshop Exploration`, `Langfuse Runtime 3`, `._assert_tenant`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `get_supabase_client()` connect `Drive Tooling` to `Memory MCP Path`, `Decision Graph 2`, `test_identity_recall.py`, `Langfuse Runtime 2`, `Test Suite`, `Workshop Exploration`, `Admissions Onboarding 7`, `MCP Integration 2`, `Decision Graph 3`, `Escalation Routes 8`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `DriveTool` connect `Admissions Onboarding 7` to `Demo Chat Lifecycle 2`, `Memory MCP Path`, `Admissions Onboarding 5`, `API Chat Schemas`, `Resource Agent 2`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 53 inferred relationships involving `get_supabase_client()` (e.g. with `main()` and `step6_tenant()`) actually correct?**
  _`get_supabase_client()` has 53 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `OnboardingFlow` (e.g. with `main()` and `AdmissionsAgent`) actually correct?**
  _`OnboardingFlow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `AgentState` (e.g. with `AdmissionsAgent` and `AdmissionsAgentResult`) actually correct?**
  _`AgentState` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `IdentityContext` (e.g. with `main()` and `main()`) actually correct?**
  _`IdentityContext` has 17 INFERRED edges - model-reasoned connections that need verification._