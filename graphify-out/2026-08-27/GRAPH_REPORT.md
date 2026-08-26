# Graph Report - Axiom-AI  (2026-08-27)

## Corpus Check
- 353 files · ~483,476 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3349 nodes · 6467 edges · 245 communities (207 shown, 38 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 1171 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b1ef5d2c`
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
- deps.py
- Dashboard Frontend Deps 4
- Dashboard Module 13
- Dashboard Module 14
- Dashboard Module 15
- test_dashboard_api.py
- useTenant
- kb_documents.py
- Demo UI
- Langfuse Runtime 7
- LangGraph Supervisor Orchestrator
- Sri Lankan Private
- check python py
- Admissions Onboarding 19
- Langfuse Runtime 8
- Phase 5 — Escalations + staff chat
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
- .create_escalation
- drive service init
- ingest service init
- src services init
- services prompts init
- rag service init
- mockData.ts
- app/page.tsx
- overview.ts
- Dashboard Alembic Dependency
- AI_API_BASE
- DASHBOARD_API_BASE
- Axiom AI Backend (README)
- MCP Adapters
- RateLimitMiddleware
- tenant_scope.py
- PaymentStatusUpdate
- FakeCrm
- Testing
- Per-institute onboarding
- FakeCrm
- conftest.py
- log.py
- seed_langfuse_prompts.py
- register_telegram_webhook.py
- smoke_mcp_memory.py
- 8. Implementation phases
- decision_bridge.py
- _page_lacks_text
- .resolve_escalation
- _load_env
- seed_langfuse_prompts.py
- rag.py
- main
- admissions_db_client.py
- validate_twilio_signature
- P2 — Telegram Bot integration
- P0 — Must finalize (MVP gate)
- register_student
- test_health.py
- send_chat_message
- get_current_staff
- _load_env
- language/__init__.py
- .list_recent_sessions

## God Nodes (most connected - your core abstractions)
1. `get_supabase_client()` - 65 edges
2. `OnboardingFlow` - 56 edges
3. `AgentState` - 53 edges
4. `IdentityContext` - 52 edges
5. `ChatChannel` - 50 edges
6. `CrmTool` - 41 edges
7. `MessageRole` - 39 edges
8. `EnrollmentStatus` - 37 edges
9. `EscalationStatus` - 37 edges
10. `RagTool` - 36 edges

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

## Communities (245 total, 38 thin omitted)

### Community 0 - "Admissions Onboarding"
Cohesion: 0.11
Nodes (20): OnboardingFlow, Determine onboarding progress and extract slots from user messages., Onboarding flow unit tests., test_awaiting_review_state(), test_class_catalog_request_on_class_step(), test_class_disambiguation_for_physics(), test_class_match_al_physics(), test_confirm_yes_completes_onboarding() (+12 more)

### Community 1 - "Admissions Onboarding 2"
Cohesion: 0.18
Nodes (19): main(), AdmissionsAgent, get_onboarding_session_store(), clear_onboarding_sessions(), FakeCrmClient, asyncio, fixture, Admissions agent node tests (in-process CRM, no MCP subprocess). (+11 more)

### Community 2 - "Demo Chat Lifecycle"
Cohesion: 0.11
Nodes (8): CrmClient, DirectCrmClient, McpCrmClient, Any, Protocol, Shared CRM client protocol for agent nodes (direct + MCP paths)., MCP CRM tools → async dispatch., In-process CRM path (dev/tests without MCP subprocesses).

### Community 3 - "RAG Ingest Pipeline"
Cohesion: 0.14
Nodes (28): qdrant_collection_for_tenant(), collection_exists(), collection_info(), count_points(), delete_collection(), _dummy_vector(), ensure_class_id_index(), ensure_collection() (+20 more)

### Community 4 - "Admissions Onboarding 3"
Cohesion: 0.06
Nodes (45): ApiError, BASE, chatApi, systemApi, App(), ChatWindow(), Props, DemoProgress() (+37 more)

### Community 5 - "RAG Ingest Pipeline 2"
Cohesion: 0.07
Nodes (42): main(), build_orchestrator(), In-process MemoryTool path (dev/tests without MCP subprocesses)., get_api_key(), _get_bool(), get_chat_model(), get_embedding_model(), _get_nested() (+34 more)

### Community 6 - "Dashboard Frontend Pages"
Cohesion: 0.07
Nodes (45): aiRequest(), assignEscalation(), BroadcastFailure, BroadcastResult, ChatSender, ChatTurn, ClassAnalyticsMetric, ClassDocumentUploadResponse (+37 more)

### Community 7 - "RAG Ingest Pipeline 3"
Cohesion: 0.14
Nodes (13): Any, RagTool, RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)., Business logic for kb_search — used by rag_server and debug REST., RAG MCP server — tool surface (same logic as axiom-rag stdio server)., test_rag_mcp_kb_ingest_status(), test_rag_mcp_kb_search_empty_collection(), test_rag_mcp_kb_search_with_citations() (+5 more)

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
Cohesion: 0.11
Nodes (21): EscalationAgent, EscalationAgentResult, _last_user_text(), Escalation agent — talk-to-tutor requests → dashboard inbox., run_escalation_agent(), _last_user_text(), PaymentAgentResult, Payment Check agent — payment receipt → escalation inbox. (+13 more)

### Community 13 - "Design Double Diamond"
Cohesion: 0.12
Nodes (17): Axiom AI Backend — Finalize Checklist, Demo UI (`demo-ui-org/`), Documentation sync, Enable Drive MCP in runtime, How to use, P1 — Demo polish, P2 — Google Drive MCP integration, Per-tenant onboarding (+9 more)

### Community 14 - "Design Double Diamond 2"
Cohesion: 0.14
Nodes (21): AuthContext, AuthContextValue, AuthProvider(), request(), AuthApiError, authRequest(), getMe(), loginStaff() (+13 more)

### Community 15 - "Admissions Onboarding 5"
Cohesion: 0.23
Nodes (35): ChatConversationsResponse, ChatConversationSummary, ChatRequest, ChatResponse, ChatThreadResponse, ChatTurnRecord, ChatTurnsResponse, ClassBroadcastRecipient (+27 more)

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
Cohesion: 0.08
Nodes (22): classify_resource_subpath(), DirectRagClient, DriveClient, _infer_drive_folder(), _last_user_text(), _mcp_text(), Any, Protocol (+14 more)

### Community 20 - "Design Double Diamond 3"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+16 more)

### Community 21 - "Decision Graph"
Cohesion: 0.11
Nodes (21): CrmTool, mock_db(), fixture, CRM tool and tenant isolation tests., test_commit_onboarding_completes_unenrolled_profile(), test_commit_onboarding_rejects_already_enrolled(), test_create_enrollment_rejects_cross_tenant_class(), test_create_enrollment_requires_consent() (+13 more)

### Community 22 - "Dashboard ORM Models"
Cohesion: 0.06
Nodes (27): AuditLog, Base, Records all staff actions performed within the system., BankSlipUpload, Base, Represents a bank slip uploaded by a student for invoice verification., Escalation, Base (+19 more)

### Community 23 - "Admissions Onboarding 7"
Cohesion: 0.05
Nodes (45): main(), smoke_drive_mock(), smoke_ingest_load(), smoke_resource_agent(), DriveTool, _normalize_drive_folder_id(), Any, Drive tool — tenant-scoped paper/textbook/syllabus search. (+37 more)

### Community 24 - "Agent Orchestrator"
Cohesion: 0.14
Nodes (16): main(), main(), ChatPipeline, Channel-agnostic chat pipeline — HTTP dev chat + Twilio webhook., Sync entry for scripts and tests without a running event loop., ChatTurnResult, InboundMessage, BaseModel (+8 more)

### Community 25 - "Admissions Onboarding 8"
Cohesion: 0.08
Nodes (25): API Design, Async Routes, Async Test Client from Day 0, Chain Dependencies, CPU Intensive Tasks, Custom Base Model, Decouple BaseSettings, Dependencies (+17 more)

### Community 26 - "Drive Tooling 2"
Cohesion: 0.09
Nodes (32): _breadcrumb(), _contextualize(), fixed_chunk(), _is_table_line(), _page_of(), parent_child_chunk(), Any, Text chunking strategies — fixed + parent-child, markdown structure aware.  Pare (+24 more)

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
Cohesion: 0.09
Nodes (33): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, _routes_from_patch(), run_chat_turn(), classify_confirmation() (+25 more)

### Community 32 - "Admissions Onboarding 10"
Cohesion: 0.17
Nodes (10): _looks_like_text(), SourceType, Detect upload format from content, not from the filename.  Both the filename and, Heuristic: decodable as UTF-8 and free of NUL bytes., Return the source type for ``content``, or raise ExtractionError.      ``filenam, sniff_format(), _zip_format(), _ooxml() (+2 more)

### Community 33 - "Resource Agent"
Cohesion: 0.16
Nodes (13): DashboardLayoutProps, ProtectedDashboard(), Header(), HeaderProps, mainNavItems, NavItem, settingsNavItem, Sidebar() (+5 more)

### Community 34 - "Chat Message Pipeline"
Cohesion: 0.11
Nodes (18): get_db(), get_tenant_id(), Authenticated tenant scope for dashboard API requests., get, root(), escalation_websocket(), websocket, create_message_log() (+10 more)

### Community 35 - "Invoice DB Layer"
Cohesion: 0.05
Nodes (37): ABC, _cache_key(), _call_gemini(), _content_type_supported(), _download_with_retry(), get_stt_metrics(), _get_twilio_auth(), InMemorySttCache (+29 more)

### Community 36 - "Design Double Diamond 4"
Cohesion: 0.11
Nodes (25): InboxContent(), isPaymentReason(), statusClass(), MessagesContent(), senderBubbleClass(), EscalationSocketEvent, EscalationSocketEventType, useEscalationSocket() (+17 more)

### Community 37 - "RAG Ingest Pipeline 5"
Cohesion: 0.24
Nodes (7): ErrorRag, FakeDrive, asyncio, User-facing resource agent reply error sanitization., test_build_resource_rag_reply_hides_internal_error(), test_kb_search_returns_generic_error_code(), test_resource_agent_rag_path_hides_search_failure()

### Community 38 - "Escalation Routes"
Cohesion: 0.11
Nodes (10): Memory business logic — called by MCP server only (Week 13 pattern)., ProceduralMemoryStore, Procedural memory store — tenant-scoped ``mem_procedures`` lookup.  Adapted from, ConversationTurn, Procedure, Memory schemas — ported from Week 13 ``memory/schemas.py`` (MVP subset)., Short-term memory store — Supabase ``st_turns`` ring buffer.  Adapted from Week, Return up to k (user, assistant) pairs — BookMe SessionStore interface. (+2 more)

### Community 39 - "Chat Message Pipeline 2"
Cohesion: 0.18
Nodes (17): classify_info_inquiry(), extract_class_filters(), format_class_details(), _format_lkr_amount(), _format_single_class(), format_staff_list(), format_tenant_info(), looks_like_institute_info() (+9 more)

### Community 40 - "Invoice DB Layer 2"
Cohesion: 0.25
Nodes (36): ChatChannel, EnrollmentStatus, EscalationStatus, ClassAnalyticsComparisonResponse, ClassAnalyticsMetric, ClassBase, ClassCreate, ClassResponse (+28 more)

### Community 41 - "Chat Message Pipeline 3"
Cohesion: 0.18
Nodes (18): main(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), preload_agent_runtime(), Any, Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., Store warmed instances from FastAPI lifespan (BookMe AI ``main.py`` pattern). (+10 more)

### Community 42 - "Dashboard ORM Models 2"
Cohesion: 0.18
Nodes (24): Base, Represents a staff member of a tuition institute., StaffUser, bootstrap_demo_physics(), login(), me(), get, Session (+16 more)

### Community 43 - "Decision Graph 2"
Cohesion: 0.26
Nodes (13): _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_conversation_thread(), get_thread_alias(), list_conversations(), Any, DashboardTenant (+5 more)

### Community 44 - "Escalation Routes 2"
Cohesion: 0.11
Nodes (19): Architecture, Dashboard overview & chat logs, Dev Chat — WhatsApp Simulator (No Twilio Required), Endpoints, Escalations (payment + talk-to-tutor), Fetch conversation history, Flow 1 — Payment receipt → dashboard inbox, Flow 2 — Talk to tutor (+11 more)

### Community 45 - "Dashboard Module"
Cohesion: 0.10
Nodes (35): BroadcastAudience, BroadcastFailure, BroadcastRecipient, BroadcastResult, class_display_name(), ClassNotFoundError, _fetch_students(), _fetch_telegram_channels() (+27 more)

### Community 46 - "Invoice DB Layer 3"
Cohesion: 0.09
Nodes (22): 10. Technical decisions, 11. Risks & mitigations, 12. Acceptance criteria, 13. Future (post-hackathon), 1. Product concept, 2. Folder structure, 3. BookMe AI → Axiom file mapping, 4. API integration (student chat) (+14 more)

### Community 47 - "CRM MCP Server"
Cohesion: 0.10
Nodes (31): build_direct_system_prompt(), build_escalation_ack_reply(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply(), build_resource_drive_list_reply(), build_resource_drive_pick_reply() (+23 more)

### Community 48 - "Escalation Routes 3"
Cohesion: 0.16
Nodes (17): emptyForm, matchesStudentSearch(), ModalMode, StudentsPage(), EnrollModal(), EnrollModalProps, StudentFormModal(), StudentFormModalProps (+9 more)

### Community 49 - "Langfuse Runtime"
Cohesion: 0.08
Nodes (25): Dashboard API Contract (Phase 5), Document ingest (knowledge base), Endpoint map, Escalation inbox (unified HITL queue), Escalation object, Get thread (message panel), How to pass tenant, Integration flow (recommended) (+17 more)

### Community 50 - "Langfuse Runtime 2"
Cohesion: 0.14
Nodes (18): main(), main(), _one_turn(), main(), get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session. (+10 more)

### Community 51 - "Test Suite"
Cohesion: 0.09
Nodes (27): _chain_mock(), main(), Dashboard chat history — legacy alias under /chat-logs., Staff reply to a student via WhatsApp.      Persists the message as role=system, send_staff_message(), assert_body_tenant(), assert_form_tenant(), assert_session_for_tenant() (+19 more)

### Community 52 - "Agent Orchestrator 3"
Cohesion: 0.12
Nodes (16): Acceptance criteria mapping, Explicitly out of scope (stay V2), Handoff checklist (dashboard team), Makefile targets (to add), Phase 6 — Implementation Plan, Risk register, Starting point (what’s already done), Suggested schedule (1 day) (+8 more)

### Community 53 - "Admissions Onboarding 11"
Cohesion: 0.32
Nodes (3): _fallback_multi(), Any, QueryRouter

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
Cohesion: 0.14
Nodes (16): ClassesPage(), ClassFormState, emptyForm, IngestContent(), TenantSelector(), TenantContext, TenantContextValue, TenantOption (+8 more)

### Community 58 - "Decision Graph 3"
Cohesion: 0.16
Nodes (22): clear_bot_token_cache(), _fetch_tenant_bot_row(), get_bot_token_for_tenant(), Any, ValueError, Per-tenant Telegram bot token lookup (SRS NFR-17 — not env vars)., Raised when a tenant has no usable Telegram bot token., Drop cached tokens — used by tests and after rotating a token. (+14 more)

### Community 59 - "Test Suite 2"
Cohesion: 0.11
Nodes (19): build_decision_graph(), decide_node(), _emit_from_config(), make_guardrail_node(), make_router_node(), Any, EmitFn, RunnableConfig (+11 more)

### Community 60 - "Student Chat Deps 4"
Cohesion: 0.24
Nodes (12): _fake_ingest_result(), _minimal_docx(), patch, Ingest pipeline unit tests., The old name is kept for one release; callers should move to run_upload_ingest., test_fixed_chunk_produces_chunks(), test_ingest_documents_parent_child(), test_load_tenant_docs_demo_physics() (+4 more)

### Community 61 - "Workshop Exploration 2"
Cohesion: 0.14
Nodes (24): main(), title_from_filename(), _attach_document_ids(), delete_document_ingest(), embed_texts(), ingest_documents(), load_tenant_docs(), prepare_upload_ingest() (+16 more)

### Community 62 - "RAG Tooling"
Cohesion: 0.14
Nodes (13): Async Routes, Core Principles, Dependency Injection, Project Structure, Pydantic Validation, python-backend, Quick Patterns, Rate Limiting (+5 more)

### Community 63 - "CRM MCP Server 2"
Cohesion: 0.17
Nodes (25): Enrollment, Base, Represents a student's enrollment in a subject class., get_class_analytics(), get_dashboard_analytics(), get_dashboard_chat_logs(), get_dashboard_escalations(), get_overview() (+17 more)

### Community 64 - "Student Chat Deps 5"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, moduleResolution, noEmit, skipLibCheck, strict, target (+3 more)

### Community 65 - "Test Suite 3"
Cohesion: 0.23
Nodes (10): FakeDrive, FakeRag, asyncio, Identity recall and resource enrollment gate tests., test_identity_resolver_keeps_enrolled_student(), test_identity_resolver_sets_human_mode_from_student(), test_identity_resolver_treats_unenrolled_row_as_visitor(), test_resource_agent_allows_pending_enrollment() (+2 more)

### Community 66 - "IdentityResolver"
Cohesion: 0.15
Nodes (17): DirectDriveClient, McpDriveClient, McpRagClient, AgentOrchestrator, AgentResponse, build_agent_mcp(), _format_session_memory(), _mcp_result_to_str() (+9 more)

### Community 67 - "Chat Message Pipeline 4"
Cohesion: 0.22
Nodes (12): ResourceAgent, FakeCrm, FakeDrive, FakeLowConfidenceRag, FakeRag, Any, asyncio, Resource agent node tests (direct tool clients, no MCP). (+4 more)

### Community 68 - "Chat Turn Runner"
Cohesion: 0.24
Nodes (16): create_student(), delete_student(), enroll_student(), get_student(), get_student_by_phone(), get_students(), delete, get (+8 more)

### Community 69 - "Langfuse Runtime 4"
Cohesion: 0.19
Nodes (12): Propagate tenant/session/user identifiers to all nested Langfuse observations., Langfuse trace scope for a WhatsApp conversation turn., Test helper — clear cached Langfuse client state., reset_langfuse_state(), trace_context(), TraceContext, Observability helper tests., setup_function() (+4 more)

### Community 70 - "MCP Integration"
Cohesion: 0.33
Nodes (8): PageText, One page of a paginated source document., _assemble(), extract_pdf(), _page_marker(), PDF → markdown via pymupdf4llm (text layer only — no vision OCR)., Extract markdown from PDF bytes using the embedded text layer only., _summarize()

### Community 71 - "Dashboard API Routes"
Cohesion: 0.18
Nodes (14): Base, Represents a tuition class offered by a tenant., SubjectClass, create_class(), delete_class(), get_class(), get_classes(), _parse_fee_cycle() (+6 more)

### Community 72 - "Escalation Routes 4"
Cohesion: 0.14
Nodes (30): assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get_tenant_escalation_or_404(), Escalation, get, put (+22 more)

### Community 73 - "Memory MCP Path"
Cohesion: 0.13
Nodes (25): _list_children(), main(), _mask_path(), _print_summary(), TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).  Does not, step10b_mcp(), step12_network(), step1_environment() (+17 more)

### Community 74 - "ShortTermMemoryStore"
Cohesion: 0.31
Nodes (6): PaymentAgent, FakeCrm, asyncio, Payment Check agent tests., test_payment_agent_creates_escalation_with_media(), test_payment_agent_requires_media()

### Community 75 - "Dashboard Module 2"
Cohesion: 0.14
Nodes (15): _format_citation_label(), format_docs(), RAG helper utilities., Format LangChain documents into a single context block., build_rag_chain(), Config, Any, RAGService (+7 more)

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
Cohesion: 0.30
Nodes (5): MessagePersistence, ChatChannel, MessageRole, Write message_logs and st_turns rows for a conversation turn., Persist a staff-authored message (role=system → sender=staff in dashboard UI).

### Community 81 - "_tracing_enabled"
Cohesion: 0.17
Nodes (17): _disable_langfuse(), get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), prefetch_prompts(), BaseException, Langfuse observability — tracing per tenant/session/user and prompt hooks.  Prom (+9 more)

### Community 82 - "Escalation Routes 6"
Cohesion: 0.18
Nodes (7): chat_result(), client(), asyncio, fixture, HTTP dev chat endpoint tests., Regression: /chat must not call asyncio.run() inside FastAPI's event loop., test_chat_pipeline_runs_agent_inside_event_loop()

### Community 83 - "Escalation Routes 7"
Cohesion: 0.17
Nodes (7): OnboardingState, Hydrate state for an existing database student (post-enrollment paths only)., OnboardingSession, OnboardingSessionStore, In-memory onboarding session store — Week 13 SessionStore pattern.  Onboarding s, Ephemeral multi-turn onboarding progress for one tenant+phone pair., Process-local store keyed by ``tenant_id:phone``.

### Community 84 - "Drive Tooling 4"
Cohesion: 0.33
Nodes (3): Any, Minimal stand-in — records whether orchestrator path runs (BookMe AI pattern)., _RecordingOrchestrator

### Community 85 - "Resource Agent 2"
Cohesion: 0.31
Nodes (9): build_conversation_summary(), phone_from_session_id(), Any, MessageRole, Shared helpers for dashboard chat endpoints., role_to_sender(), turn_to_record(), ChatTurnRecord (+1 more)

### Community 86 - "Dashboard Module 3"
Cohesion: 0.28
Nodes (5): normalize_markdown(), Clean up extractor output so headings are usable as breadcrumbs.      Layout-der, Format sniffing, DOCX/markdown extraction, and PDF text-layer routing., test_title_from_filename(), TestNormalizeMarkdown

### Community 87 - "Dashboard API Routes 2"
Cohesion: 0.18
Nodes (9): ExtractedDoc, ExtractionError, ValueError, Shared types for document extraction.  Every extractor converts source bytes int, Raised when a document cannot be turned into usable markdown.      Subclasses Va, Normalized extraction result handed to the ingest pipeline., extract_markdown(), Markdown / plain-text passthrough. (+1 more)

### Community 88 - "MCP Integration 2"
Cohesion: 0.14
Nodes (15): IdentityContext, Resolved tenant + student scope for one WhatsApp conversation., Resolved tenant scope; student_id is set only when a DB record exists., Stable recall key — student id when enrolled, otherwise phone., Past papers and RAG require pending or active enrollment., build_recall_context(), format_student_profile(), Build recall context (student profile + ST turns) before the decision graph. (+7 more)

### Community 89 - "Test Suite 4"
Cohesion: 0.12
Nodes (15): 10. Known Sandbox Limitations to Flag (be upfront about these, don't get caught off guard), 1. Account Setup (15–30 min), 2. How the Flow Maps to Your Existing Architecture, 3. Install Dependencies, 4. Build the Webhook Endpoint, 5. Critical Constraint: The 3-Second Webhook Window, 6. Exposing Your Local Backend to Twilio (for testing before deployment), 7. Handling Voice Notes (ties into your P0 voice transcription feature) (+7 more)

### Community 90 - "Test Suite 5"
Cohesion: 0.18
Nodes (7): parse_twilio_form(), Parse Twilio application/x-www-form-urlencoded webhook bodies., client(), identity_ctx(), fixture, Twilio webhook endpoint tests., test_parse_twilio_form_extracts_media()

### Community 92 - "TwilioMessagingClient"
Cohesion: 0.23
Nodes (8): extract_docx(), _heading_level(), _looks_like_heading(), _promote_bold_headings(), DOCX → markdown via mammoth (HTML) → markdownify.  mammoth keys off Word's *sema, Turn standalone whole-line bold paragraphs into markdown headings., Extract markdown from .docx bytes., TestPromoteBoldHeadings

### Community 93 - "Escalation Routes 8"
Cohesion: 0.07
Nodes (42): bind_telegram_student_channel(), _delete_pending(), _has_enrollment(), link_telegram_contact(), _lookup_pending_phone(), _lookup_student_by_phone(), _parse_channel(), _pending_identity() (+34 more)

### Community 94 - "test_twilio_webhook.py"
Cohesion: 0.29
Nodes (9): _parse_form_params(), BackgroundTasks, Request, Response, Twilio WhatsApp webhook router., Twilio WhatsApp sandbox webhook.      Returns 200 immediately and processes the, _should_validate_signature(), twilio_webhook() (+1 more)

### Community 96 - "Dashboard Module 4"
Cohesion: 0.47
Nodes (9): _chat(), main(), _phone(), _require_live_env(), scenario_escalation(), scenario_onboarding(), scenario_out_of_scope(), scenario_payment() (+1 more)

### Community 97 - "Escalation Routes 11"
Cohesion: 0.31
Nodes (9): add_turn(), get_procedural(), _init(), tool, Memory MCP Server — exposes ST recall / add_turn / procedural lookup.  Adapted f, Fetch recent conversation turns for a tenant session., Append a conversation turn to short-term memory., Lookup tenant onboarding / workflow procedures. (+1 more)

### Community 98 - "Demo Chat Lifecycle 2"
Cohesion: 0.14
Nodes (19): DrivePickFile, DrivePickSession, DrivePickStore, files_from_drive_payload(), get_drive_pick_store(), parse_file_pick_index(), Any, datetime (+11 more)

### Community 99 - "Admissions Onboarding 16"
Cohesion: 0.22
Nodes (8): AGENTS.md — Axiom AI Backend, Environment, Gotchas, Linting, LLM Providers, Project Structure, Quick Commands, Testing

### Community 100 - "Escalation Routes 12"
Cohesion: 0.13
Nodes (15): 11. API Contract Summary (Dashboard Team), 12. Environment Variables, 13. Explicitly Out of MVP Scope, 14. Per-Phase Workflow, 15. Day-by-Day Schedule, 1. Locked Architecture Decisions, 6. Resource Split: Google Drive vs RAG, 9. High-Level Architecture (+7 more)

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
Cohesion: 0.17
Nodes (18): ChatChannel, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, MessageRole, PaymentStatus, Enum (+10 more)

### Community 105 - "Admissions Onboarding 18"
Cohesion: 0.11
Nodes (23): detect_script_language(), language_policy_block(), Reply-language resolution for Sinhala, Tamil, English, and code-switching.  Nati, Return si/ta when native script is present; None for Latin-only text., Script of this message wins; otherwise stored preference; otherwise English., Human-readable hint for STT. None for English so Gemini auto-detects., Mandatory generation rule appended to LLM-facing system prompts., resolve_reply_language() (+15 more)

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
Cohesion: 0.21
Nodes (11): FakeDrive, Any, asyncio, patch, Class-scoped RAG retrieval tests., test_kb_search_forwards_class_ids_to_rag_service(), test_resource_agent_blocks_enrolled_without_class_ids(), test_resource_agent_passes_enrolled_class_ids_to_rag() (+3 more)

### Community 112 - "Dashboard Module 6"
Cohesion: 0.15
Nodes (21): _dispatch(), Any, Request, Telegram Bot API webhook router — one bot (token) per tenant., Receive Telegram updates for a single tenant bot.      Always acknowledges with, telegram_webhook(), _display_name(), _ensure_onboarding_session() (+13 more)

### Community 113 - "RAG Ingest Pipeline 7"
Cohesion: 0.33
Nodes (8): main(), _mock_drive_backend(), Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)., Paper query → Drive link (mock backend; no Google credentials)., Velocity query → cited RAG answer (mocked RAG service)., smoke_drive_paper_link(), smoke_rag_velocity_live(), smoke_rag_velocity_mock()

### Community 114 - "escalation_reasons.py"
Cohesion: 0.18
Nodes (16): delete_document(), get_document(), list_documents(), BackgroundTasks, DashboardTenant, delete, get, Document ingest — PDF/DOCX/Markdown upload → parent-child chunk → Qdrant. (+8 more)

### Community 115 - "Langfuse Runtime 6"
Cohesion: 0.12
Nodes (12): get, FastAPI application — Phase 6 integration (MCP warmup + dashboard APIs)., root(), BaseHTTPMiddleware, Request, Response, Request ID and latency headers., RequestContextMiddleware (+4 more)

### Community 116 - "Dashboard Module 7"
Cohesion: 0.29
Nodes (7): PaymentStatusUpdate, Example dashboard PATCH body using domain enums., parametrize, test_enum_values(), test_payment_status_update_accepts_enum(), test_payment_status_update_rejects_invalid(), test_tenant_summary_schema()

### Community 117 - "Dashboard Module 8"
Cohesion: 0.29
Nodes (4): db_conn(), _db_url(), fixture, Validate v2 ER schema tables exist in Supabase when DATABASE_URL is configured.

### Community 118 - "Student Chat Deps 6"
Cohesion: 0.17
Nodes (12): AnalyticsPage(), humanizeReason(), OverviewPage(), ChartCard(), ChartCardProps, MetricCard(), MetricCardProps, DashboardAnalytics (+4 more)

### Community 119 - "Demo Chat Lifecycle 3"
Cohesion: 0.29
Nodes (7): get_broadcast_recipients(), post_class_broadcast(), DashboardTenant, get, Staff class broadcast to Telegram-linked students., Preview who would receive a Telegram class announcement., Send a class announcement to Telegram-linked enrolled students.

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
Cohesion: 0.40
Nodes (5): get_chat_logs(), ChatTurnsResponse, DashboardTenant, get, Legacy path for conversation history.      Prefer `GET /dashboard/chat/conversat

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
Cohesion: 0.17
Nodes (12): 10. Phased Implementation Plan, Acceptance Criteria, Acceptance Criteria, Features, Features, Files / Modules, Objective, Objective (+4 more)

### Community 128 - "Dashboard API Routes 4"
Cohesion: 0.16
Nodes (15): compute_document_id(), point_id_for_chunk(), point_id_for_parent(), Stable document and point identity for idempotent Qdrant ingest., Content hash — same bytes always yield the same id within a tenant., Deterministic Qdrant point id so re-ingest replaces rather than duplicates., Deterministic id for a parent-context point (stored once, joined on retrieval)., patch (+7 more)

### Community 129 - "Student Chat Deps 7"
Cohesion: 0.35
Nodes (5): AdmissionsAgentResult, _last_user_text(), Any, Admissions agent node — multi-turn onboarding via CRM MCP tools., run_admissions_agent()

### Community 130 - "Decision Graph 4"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 131 - "Supabase DB Client 6"
Cohesion: 0.33
Nodes (6): 8.1 Agentic Workforce and Conversational Interface, 8.2 Financial and Ticket Management, 8.3 Administrative Dashboard and Agency CRM, 8.5 Marketing and Lead Management, 8.6 Platform Administration and Multi-Tenancy (New), 8\. Functional Requirements

### Community 132 - "P0 — Must finalize (MVP gate)"
Cohesion: 0.29
Nodes (7): delete_chunks_by_document_id(), ensure_document_id_index(), Keyword index on document_id for idempotent delete-before-upsert., Remove all Qdrant points belonging to one ingested document., Exclude parent-context points from vector search — they are joined by id., _search_filter(), Filter

### Community 133 - "preload agent runtime"
Cohesion: 0.33
Nodes (5): list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant.

### Community 134 - "page_needs_ocr"
Cohesion: 0.33
Nodes (5): list_tenants(), ping_supabase(), Any, Supabase REST client wrapper., Lightweight connectivity check via tenants table.

### Community 135 - "test_run_resource_agent_requires_mcp_clients_when_fallback_disabled"
Cohesion: 0.36
Nodes (7): _init(), kb_ingest_status(), kb_search(), tool, RAG MCP Server — tenant-scoped tutor-note Q&A., Search tutor lesson notes (Qdrant) and return a grounded answer with citations., Return Qdrant ingest status for a tenant's tutor-note collection.

### Community 136 - "Dashboard Frontend Deps 3"
Cohesion: 0.13
Nodes (15): heuristic_route(), _normalize_action(), _pattern_score(), Query Router — LLM intent classification for tuition agents.  Ported from BookMe, Deterministic routing for unambiguous tuition intents (before LLM)., AgentState — shared LangGraph state for the Axiom orchestrator.  Ported from Boo, parametrize, Keyword heuristic router tests (no LLM). (+7 more)

### Community 137 - "deps.py"
Cohesion: 0.14
Nodes (14): get_drive_tool(), get_rag_tool(), get_request_id(), Request, FastAPI dependency injection helpers., _require_startup(), list_files(), Debug REST — Drive tool (same surface as drive_server MCP). (+6 more)

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

### Community 142 - "test_dashboard_api.py"
Cohesion: 0.32
Nodes (11): _chain_mock(), patch, Dashboard API HTTP tests (mocked Supabase + CRM)., test_dashboard_chat_conversations(), test_dashboard_chat_logs_alias(), test_dashboard_chat_thread(), test_dashboard_overview(), test_dashboard_staff_send_returns_502_when_delivery_fails() (+3 more)

### Community 143 - "useTenant"
Cohesion: 0.18
Nodes (13): profileToForm(), SettingsFormState, SettingsPage(), ToastContainer(), toastStyles(), Toast, ToastContext, ToastContextValue (+5 more)

### Community 144 - "kb_documents.py"
Cohesion: 0.40
Nodes (9): delete_document(), get_document(), list_documents(), mark_failed(), _now_iso(), Any, Supabase registry for ingested tutor documents., registry_available() (+1 more)

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
Cohesion: 0.36
Nodes (7): active_config(), health(), get, Request, Health, readiness, and config endpoints., ready(), HealthResponse

### Community 152 - "Phase 5 — Escalations + staff chat"
Cohesion: 0.29
Nodes (9): admissions_route_decision(), apply_onboarding_patch_overrides(), is_onboarding_active(), onboarding_router_context_hint(), Route-lock helpers — keep mid-onboarding turns on the admissions agent., True when a clear specialist intent should override active onboarding., True when an in-memory onboarding session is collecting details., Force proceed + admissions when mid-onboarding. Returns True if applied. (+1 more)

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

### Community 160 - "Chat Message Pipeline 7"
Cohesion: 0.31
Nodes (9): get_current_trace_id(), langfuse_turn_attributes(), Any, OpenTelemetry / Langfuse trace id for the active context, if any., Propagate user/session/tags to nested spans for one chat turn., Attach I/O + usage to the current span/generation., _tracing_enabled(), update_current_observation() (+1 more)

### Community 214 - "RateLimitMiddleware"
Cohesion: 0.36
Nodes (4): BaseHTTPMiddleware, Request, Response, RateLimitMiddleware

### Community 215 - "tenant_scope.py"
Cohesion: 0.29
Nodes (7): _count_rows(), dashboard_overview(), Any, DashboardTenant, get, Dashboard overview stats for staff home screen., Aggregate counts for dashboard landing page.

### Community 216 - "PaymentStatusUpdate"
Cohesion: 0.22
Nodes (8): FeeCycle, InvoiceStatus, Enum, str, Domain status enums — mirror PostgreSQL ENUM types in sql/01_schema.sql., StaffRole, Domain types — enums and value objects., Persist inbound/outbound messaging to Supabase (message_logs + st_turns).

### Community 217 - "FakeCrm"
Cohesion: 0.32
Nodes (5): ClassAnalyticsPage(), formatClassTitle(), SortKey, ClassAnalyticsComparison, getClassAnalytics()

### Community 218 - "Testing"
Cohesion: 0.38
Nodes (6): active_tenant_scope(), client(), client_no_tenant_override(), fixture, Shared pytest bootstrap., # IMPORTANT:

### Community 219 - "Per-institute onboarding"
Cohesion: 0.20
Nodes (4): _format_lkr_amount(), OnboardingSlots, Any, Multi-turn admissions onboarding — slot tracking and class disambiguation.

### Community 220 - "FakeCrm"
Cohesion: 0.33
Nodes (4): FakeCrm, asyncio, Escalation agent tests., test_escalation_agent_creates_talk_to_tutor_ticket()

### Community 221 - "conftest.py"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features *(original plan — see PHASE5_DECISIONS.md for what changed)*, Files / Modules, Objective, Phase 5 — Payment Check, Escalation & Dashboard APIs, Reference Implementation (copy — do not invent)

### Community 223 - "seed_langfuse_prompts.py"
Cohesion: 0.25
Nodes (16): _ingest_result(), _minimal_docx(), _post(), patch, Multi-format ingest upload endpoint tests., test_delete_ingest_document(), test_get_ingest_document(), test_ingest_upload_docx() (+8 more)

### Community 225 - "smoke_mcp_memory.py"
Cohesion: 0.60
Nodes (5): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory()

### Community 226 - "8. Implementation phases"
Cohesion: 0.21
Nodes (11): TenantStatus, Base, Represents a tuition institute (tenant) in the Axiom AI platform.     Every busi, Tenant, get_tenant_profile(), list_tenants(), _normalize_slug(), get (+3 more)

### Community 227 - "decision_bridge.py"
Cohesion: 0.15
Nodes (17): main(), _primary_route(), RoutingCase, _run(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, build_decision_input(), DecisionState (+9 more)

### Community 228 - "_page_lacks_text"
Cohesion: 0.43
Nodes (3): _page_lacks_text(), True when a page's text layer yielded too little to be real content., TestPageLacksText

### Community 229 - ".resolve_escalation"
Cohesion: 0.15
Nodes (7): Open (or return existing) escalation for dashboard inbox., Legacy alias — creates payment_receipt escalation without bank_slip storage., Reason-aware resolve: payment → activate enrollment; tutor → close only., Staff approves payment — activates pending enrollment., Staff rejects payment — closes escalation without activating enrollment., Backward-compatible alias for payment resolve., is_payment_reason()

### Community 231 - "seed_langfuse_prompts.py"
Cohesion: 0.60
Nodes (4): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog()

### Community 232 - "rag.py"
Cohesion: 0.35
Nodes (4): IdentityResolver, Any, Lookup tenant by sandbox number and student by sender phone., Resolve identity for HTTP dev chat when tenant_id is known.

### Community 233 - "main"
Cohesion: 0.29
Nodes (4): AdminRegistration, StaffRegistration, EmailStr, field_validator

### Community 234 - "admissions_db_client.py"
Cohesion: 0.33
Nodes (3): CRM business logic — called by MCP server only (Week 13 pattern)., Escalation reason codes for dashboard inbox filtering., Supabase access for admissions CRM operations.

### Community 235 - "validate_twilio_signature"
Cohesion: 0.33
Nodes (7): Twilio request signature validation., validate_twilio_signature(), Twilio signature validation tests., _sign(), test_validate_twilio_signature_accepts_valid_signature(), test_validate_twilio_signature_rejects_invalid_signature(), test_validate_twilio_signature_rejects_tampered_body()

### Community 236 - "P2 — Telegram Bot integration"
Cohesion: 0.25
Nodes (8): Agent pipeline, Bot & environment, Documentation, Identity & persistence, Inbound webhook, Outbound messaging, P2 — Telegram Bot integration, Testing

### Community 237 - "P0 — Must finalize (MVP gate)"
Cohesion: 0.25
Nodes (8): Core agent & routing, Dashboard handoff, Error handling (Phase 6 WS5), Langfuse, Live infrastructure, P0 — Must finalize (MVP gate), Phase 6 E2E scripts, RAG (tutor notes)

### Community 238 - "register_student"
Cohesion: 0.32
Nodes (7): get_student(), Any, get, Student registration and lookup — dashboard + dev API., Register or update a student profile (dashboard / manual onboarding)., Fetch student profile and enrollments by phone., register_student()

### Community 239 - "test_health.py"
Cohesion: 0.25
Nodes (3): client(), fixture, Phase 0 health endpoint tests.

### Community 240 - "send_chat_message"
Cohesion: 0.33
Nodes (5): HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required)., Send a student message and receive an AI reply.      Use this during development, send_chat_message(), ChatRequest, ChatResponse

### Community 241 - "get_current_staff"
Cohesion: 0.50
Nodes (4): get_current_staff(), Session, decode_access_token(), HTTPAuthorizationCredentials

## Knowledge Gaps
- **626 isolated node(s):** `name`, `private`, `version`, `type`, `description` (+621 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CrmTool` connect `Decision Graph` to `Demo Chat Lifecycle`, `.resolve_escalation`, `admissions_db_client.py`, `register_student`, `Admissions Onboarding 6`, `.create_escalation`, `Drive Tooling`, `Workshop Exploration`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `get_supabase_client()` connect `Drive Tooling` to `Decision Graph 3`, `page_needs_ocr`, `Escalation Routes`, `rag.py`, `Memory MCP Path`, `Decision Graph 2`, `Dashboard Module`, `kb_documents.py`, `test_identity_recall.py`, `Langfuse Runtime 2`, `Test Suite`, `.list_recent_sessions`, `Workshop Exploration`, `Admissions Onboarding 7`, `tenant_scope.py`, `Escalation Routes 8`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `OnboardingFlow` connect `Admissions Onboarding` to `Admissions Onboarding 2`, `Student Chat Deps 7`, `CRM MCP Server`, `Escalation Routes 7`, `Workshop Exploration`, `Per-institute onboarding`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `get_supabase_client()` (e.g. with `main()` and `step6_tenant()`) actually correct?**
  _`get_supabase_client()` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `OnboardingFlow` (e.g. with `main()` and `AdmissionsAgent`) actually correct?**
  _`OnboardingFlow` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `AgentState` (e.g. with `AdmissionsAgent` and `AdmissionsAgentResult`) actually correct?**
  _`AgentState` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `IdentityContext` (e.g. with `main()` and `main()`) actually correct?**
  _`IdentityContext` has 24 INFERRED edges - model-reasoned connections that need verification._