# Graph Report - Axiom-AI  (2026-08-28)

## Corpus Check
- 415 files · ~525,907 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4242 nodes · 8738 edges · 272 communities (230 shown, 42 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 1704 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `04188554`
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
- Supabase DB Client 4
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
- build_cors_origins
- test_run_resource_agent_requires_mcp_clients_when_fallback_disabled
- Dashboard Frontend Deps 3
- deps.py
- Dashboard Frontend Deps 4
- Dashboard Module 13
- Dashboard Module 14
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
- Dashboard Module 19
- Dashboard Module 20
- Dashboard Module 21
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
- tests init py
- mockData.ts
- payments/page.tsx
- app/page.tsx
- overview.ts
- postcss.config.js
- student-chat/tailwind.config.js
- Project Planning.md
- agents/tools/__init__.py
- api/__init__.py
- routers/__init__.py
- routers/tools/__init__.py
- webhooks/__init__.py
- db/__init__.py
- mcp_servers/__init__.py
- memory/__init__.py
- drive_service/__init__.py
- ingest_service/__init__.py
- src/services/__init__.py
- services/prompts/__init__.py
- rag_service/__init__.py
- tests/__init__.py
- deps/__init__.py
- Dashboard Alembic Dependency
- CLAUDE.md
- AI_API_BASE
- DASHBOARD_API_BASE
- frontend/tailwind.config.js
- Axiom AI Backend (README)
- MCP Adapters
- RateLimitMiddleware
- tenant_scope.py
- PaymentStatusUpdate
- FakeCrm
- Testing
- telegram_webhook
- register_student
- conftest.py
- log.py
- seed_langfuse_prompts.py
- register_telegram_webhook.py
- smoke_mcp_memory.py
- 8. Implementation phases
- agent.py
- .resolve_escalation
- _load_env
- seed_langfuse_prompts.py
- rag.py
- log.py
- validate_twilio_signature
- P2 — Telegram Bot integration
- drive_server.py
- analytics_start_date
- test_health.py
- escalation_reasons.py
- send_chat_message
- get_current_staff
- supabase_client.py
- language/__init__.py
- .list_recent_sessions
- smoke_resource.py
- get_chat_logs
- send_chat_message
- field_definitions.py
- _one_turn
- .list_recent_sessions
- get_api_key
- schedule/__init__.py
- delete_chunks_by_document_id
- test_drive_mcp_server.py
- classify_media
- smoke_mcp_memory.py
- test_media_kind.py
- telegram_webhook
- validate_twilio_signature
- arithmetic.py
- main
- ClassReference
- Per-institute onboarding
- smoke_resource.py
- rag.py
- debug_google_auth.py
- bench_nlu.py
- examples.py
- nlu/__init__.py

## God Nodes (most connected - your core abstractions)
1. `OnboardingFlow` - 81 edges
2. `get_supabase_client()` - 75 edges
3. `IdentityContext` - 68 edges
4. `AgentState` - 59 edges
5. `DayOfWeek` - 58 edges
6. `OccurrenceStatus` - 55 edges
7. `ChatChannel` - 54 edges
8. `ScheduleStatus` - 54 edges
9. `ScheduleService` - 53 edges
10. `MessageRole` - 50 edges

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

## Communities (272 total, 42 thin omitted)

### Community 0 - "Admissions Onboarding"
Cohesion: 0.11
Nodes (36): parse_field_definitions(), Turn DB/CRM rows into field defs, skipping reserved core keys., TenantFieldDef, OnboardingFlow, Determine onboarding progress and extract slots from user messages., _assert_collection_restarted(), _awaiting_confirmation_state(), Onboarding flow unit tests. (+28 more)

### Community 1 - "Admissions Onboarding 2"
Cohesion: 0.05
Nodes (81): AdmissionsAgent, AdmissionsAgentResult, _class_label(), _last_user_text(), Any, Admissions agent node — multi-turn onboarding via CRM MCP tools., Answer "I want to join X" against real enrollment rows (B1, B2).          Which, Append the unfinished flow's reminder to an interrupting answer. (+73 more)

### Community 2 - "Demo Chat Lifecycle"
Cohesion: 0.09
Nodes (9): main(), CrmClient, DirectCrmClient, McpCrmClient, Any, Protocol, Shared CRM client protocol for agent nodes (direct + MCP paths)., MCP CRM tools → async dispatch. (+1 more)

### Community 3 - "RAG Ingest Pipeline"
Cohesion: 0.10
Nodes (38): qdrant_collection_for_tenant(), collection_exists(), collection_info(), count_points(), delete_chunks_by_document_id(), delete_collection(), _dummy_vector(), ensure_class_id_index() (+30 more)

### Community 4 - "Admissions Onboarding 3"
Cohesion: 0.06
Nodes (45): ApiError, BASE, chatApi, systemApi, App(), ChatWindow(), Props, DemoProgress() (+37 more)

### Community 2 - "Demo Chat Lifecycle"
Cohesion: 0.07
Nodes (43): bind_telegram_student_channel(), _delete_pending(), _has_enrollment(), link_telegram_contact(), _lookup_pending_phone(), _lookup_student_by_phone(), _parse_channel(), _pending_identity() (+35 more)

### Community 3 - "RAG Ingest Pipeline"
Cohesion: 0.05
Nodes (45): main(), smoke_drive_mock(), smoke_ingest_load(), smoke_resource_agent(), DriveTool, _normalize_drive_folder_id(), Any, Drive tool — tenant-scoped paper/textbook/syllabus search. (+37 more)

### Community 4 - "Admissions Onboarding 3"
Cohesion: 0.05
Nodes (34): _chain_mock(), main(), assert_body_tenant(), Resolved, active tenant — all dashboard queries must use this scope., Reject POST bodies whose tenant_id does not match the resolved scope., TenantScope, mock_client(), MockSupabaseClient (+26 more)

### Community 5 - "RAG Ingest Pipeline 2"
Cohesion: 0.08
Nodes (40): profileToForm(), SettingsFormState, SettingsPage(), defaultOnboardingFields(), DraftOnboardingField, RegisterPage(), RESERVED_FIELD_KEYS, AuthContext (+32 more)

### Community 6 - "Dashboard Frontend Pages"
Cohesion: 0.08
Nodes (13): main(), CrmClient, DirectCrmClient, McpCrmClient, Any, Protocol, Shared CRM client protocol for agent nodes (direct + MCP paths)., MCP CRM tools → async dispatch. (+5 more)

### Community 7 - "RAG Ingest Pipeline 3"
Cohesion: 0.09
Nodes (25): main(), _mock_drive_backend(), Velocity query → cited RAG answer (mocked RAG service)., Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)., Paper query → Drive link (mock backend; no Google credentials)., smoke_drive_paper_link(), smoke_rag_velocity_live(), smoke_rag_velocity_mock() (+17 more)

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
Cohesion: 0.09
Nodes (23): Application Access Patterns, Apply schema, Axiom AI — Database Documentation, Demo Seed Data, ENUM Types, ER Diagram, ER entity → SQL table mapping, Legacy v1 Tables (removed) (+15 more)

### Community 12 - "Admissions Onboarding 4"
Cohesion: 0.33
Nodes (4): FakeCrm, asyncio, Escalation agent tests., test_escalation_agent_creates_talk_to_tutor_ticket()

### Community 13 - "Design Double Diamond"
Cohesion: 0.06
Nodes (33): Agent pipeline, Axiom AI Backend — Finalize Checklist, Bot & environment, Core agent & routing, Dashboard handoff, Demo UI (`demo-ui-org/`), Documentation, Documentation sync (+25 more)

### Community 14 - "Design Double Diamond 2"
Cohesion: 0.08
Nodes (39): profileToForm(), SettingsFormState, SettingsPage(), defaultOnboardingFields(), DraftOnboardingField, RegisterPage(), RESERVED_FIELD_KEYS, AuthContext (+31 more)

### Community 15 - "Admissions Onboarding 5"
Cohesion: 0.21
Nodes (55): list_files(), Debug REST — Drive tool (same surface as drive_server MCP)., search(), ChatConversationsResponse, ChatConversationSummary, ChatRequest, ChatResponse, ChatThreadResponse (+47 more)

### Community 8 - "Student Chat Deps"
Cohesion: 0.07
Nodes (43): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog(), RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)., _disable_langfuse(), flush(), get_current_trace_id() (+35 more)

### Community 9 - "RAG Ingest Pipeline 4"
Cohesion: 0.08
Nodes (24): DirectDriveClient, DirectScheduleClient, _format_day_schedule(), _format_schedule_reply(), _format_single_class(), _format_week_schedule(), _mcp_text(), McpDriveClient (+16 more)

### Community 10 - "Student Chat Deps 2"
Cohesion: 0.08
Nodes (35): ClassAnalyticsPage(), formatClassTitle(), PERIOD_OPTIONS, SortKey, SummaryCard(), AnalyticsPage(), humanizeReason(), PERIOD_OPTIONS (+27 more)

### Community 11 - "Student Chat Deps 3"
Cohesion: 0.08
Nodes (31): main(), main(), main(), Send a student message and receive an AI reply.      Use this during development, send_chat_message(), IdentityContext, Resolved tenant + student scope for one WhatsApp conversation., Resolved tenant scope; student_id is set only when a DB record exists. (+23 more)

### Community 12 - "Admissions Onboarding 4"
Cohesion: 0.08
Nodes (37): cancel_schedule(), create_exception(), create_schedule(), delete_exception(), get_schedule(), list_exceptions(), list_schedules(), DashboardTenant (+29 more)

### Community 13 - "Design Double Diamond"
Cohesion: 0.09
Nodes (39): main(), _primary_route(), RoutingCase, _run(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, build_decision_graph(), build_decision_input() (+31 more)

### Community 14 - "Design Double Diamond 2"
Cohesion: 0.04
Nodes (46): 0.1 Shared secrets, 0.2 Google Drive (platform), 0.3 Twilio (platform), 0.4 Langfuse (platform), 0.5 Three processes must be running for dashboard + chat, 1.1 Apply AI-backend SQL (lexical order), 1.2 Apply Dashboard staff-auth columns (not in `init-db`), 1.3 RLS (+38 more)

### Community 15 - "Admissions Onboarding 5"
Cohesion: 0.04
Nodes (44): dependencies, clsx, framer-motion, lucide-react, react, react-dom, react-markdown, remark-gfm (+36 more)

### Community 16 - "Dashboard Frontend Deps"
Cohesion: 0.06
Nodes (27): AuditLog, Base, Records all staff actions performed within the system., BankSlipUpload, Base, Represents a bank slip uploaded by a student for invoice verification., Escalation, Base (+19 more)

### Community 17 - "Admissions Onboarding 6"
Cohesion: 0.10
Nodes (24): _last_user_text(), PaymentAgentResult, Payment Check agent — payment receipt → escalation inbox., run_payment_agent(), AgentOrchestrator, _emit_from_config(), _format_session_memory(), _invoke_llm_text() (+16 more)

### Community 18 - "Drive Tooling"
Cohesion: 0.17
Nodes (5): get_supabase_client(), Return a singleton Supabase client (requires service role key)., AdmissionsDbClient, Any, Tenant-scoped student, class, and enrollment persistence.

### Community 19 - "API Chat Schemas"
Cohesion: 0.07
Nodes (28): DirectDriveClient, DirectScheduleClient, DriveClient, _format_day_schedule(), _format_schedule_reply(), _format_single_class(), _format_week_schedule(), _mcp_text() (+20 more)

### Community 20 - "Design Double Diamond 3"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+16 more)

### Community 21 - "Decision Graph"
Cohesion: 0.10
Nodes (23): CrmTool, mock_db(), fixture, CRM tool and tenant isolation tests., test_commit_onboarding_completes_unenrolled_profile(), test_commit_onboarding_rejects_already_enrolled(), test_commit_onboarding_writes_extra_fields(), test_create_enrollment_rejects_cross_tenant_class() (+15 more)

### Community 22 - "Dashboard ORM Models"
Cohesion: 0.05
Nodes (33): AuditLog, Base, Records all staff actions performed within the system., BankSlipUpload, Base, Represents a bank slip uploaded by a student for invoice verification., Escalation, Base (+25 more)

### Community 23 - "Admissions Onboarding 7"
Cohesion: 0.13
Nodes (19): build_drive_backend(), DriveBackend, find_child_folder(), GoogleDriveBackend, MockDriveBackend, normalize_folder_compact(), normalize_folder_key(), _prefer_ipv4_for_urllib3() (+11 more)

### Community 24 - "Agent Orchestrator"
Cohesion: 0.17
Nodes (10): main(), ChatTurnResult, BaseModel, Messaging payload schemas — Twilio + channel-agnostic chat., Result of one chat turn — used by HTTP and Twilio paths., TwilioInboundMessage, TwilioSendResult, Thin wrapper around Twilio Messages API with dry-run support. (+2 more)

### Community 25 - "Admissions Onboarding 8"
Cohesion: 0.08
Nodes (25): API Design, Async Routes, Async Test Client from Day 0, Chain Dependencies, CPU Intensive Tasks, Custom Base Model, Decouple BaseSettings, Dependencies (+17 more)

### Community 26 - "Drive Tooling 2"
Cohesion: 0.08
Nodes (33): _breadcrumb(), _contextualize(), fixed_chunk(), _is_table_line(), _page_of(), parent_child_chunk(), Any, Text chunking strategies — fixed + parent-child, markdown structure aware.  Pare (+25 more)

### Community 27 - "Supabase DB Client"
Cohesion: 0.08
Nodes (23): Basic Setup, Batch Messages, Best Practices, FastAPI Caching, FastAPI Rate Limiting, FastAPI Session Management, Hash Operations, Key Expiration (TTL) (+15 more)

### Community 28 - "Agent Orchestrator 2"
Cohesion: 0.11
Nodes (18): 1. Google Cloud, 2. Environment, Architecture, Google Drive MCP — Integration & Testing, Multi-tenant isolation, MVP vs v2, Onboarding checklist, Phase 4 closure (+10 more)

### Community 29 - "Drive Tooling 3"
Cohesion: 0.09
Nodes (22): 10. Deferred to Phase 3+, 1. Where we are today, 2. Binding constraint: no torch in the runtime image, 3. Target architecture, 4. Chunking upgrade, 5. Phase 1 — extraction router, 6. Phase 2 — correctness and lifecycle, 7. Configuration (+14 more)

### Community 30 - "Identity Context"
Cohesion: 0.09
Nodes (22): Alembic Migration Naming, Async Engine + Session, Bulk Insert, Bulk Operations, Bulk Update, Cascade Delete, Commit/Rollback Pattern, Constraint Naming (+14 more)

### Community 31 - "Admissions Onboarding 9"
Cohesion: 0.09
Nodes (33): ChatResult, _is_slip_candidate(), _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, Remind the student of the flow their message interrupted.      Interrupting a fl, Whether an attachment should be routed to payment verification.      An unclassi (+25 more)

### Community 32 - "Admissions Onboarding 10"
Cohesion: 0.15
Nodes (11): _looks_like_text(), SourceType, Detect upload format from content, not from the filename.  Both the filename and, Heuristic: decodable as UTF-8 and free of NUL bytes., Return the source type for ``content``, or raise ExtractionError.      ``filenam, sniff_format(), _zip_format(), _ooxml() (+3 more)

### Community 33 - "Resource Agent"
Cohesion: 0.16
Nodes (13): DashboardLayoutProps, ProtectedDashboard(), Header(), HeaderProps, mainNavItems, NavItem, settingsNavItem, Sidebar() (+5 more)

### Community 34 - "Chat Message Pipeline"
Cohesion: 0.10
Nodes (20): AdminRegistration, OnboardingFieldInput, field_validator, StaffRegistration, FieldConfigLockedError, Session, ValueError, Persist and lock per-tenant onboarding field definitions. (+12 more)

### Community 35 - "Invoice DB Layer"
Cohesion: 0.16
Nodes (11): _get_twilio_auth(), _is_audio_url(), _mask_phone(), _measure_audio_duration(), Speech-to-text service — download voice notes and transcribe via Gemini.  Featur, Mask phone number: +9477****567. Returns 'unknown' if None., Check if a URL points to a voice note file (.ogg/.opus) based on extension., Return (account_sid, auth_token) if configured, else None. (+3 more)

### Community 36 - "Design Double Diamond 4"
Cohesion: 0.11
Nodes (25): InboxContent(), isPaymentReason(), statusClass(), MessagesContent(), senderBubbleClass(), EscalationSocketEvent, EscalationSocketEventType, useEscalationSocket() (+17 more)

### Community 37 - "RAG Ingest Pipeline 5"
Cohesion: 0.19
Nodes (12): Propagate tenant/session/user identifiers to all nested Langfuse observations., Langfuse trace scope for a WhatsApp conversation turn., Test helper — clear cached Langfuse client state., reset_langfuse_state(), trace_context(), TraceContext, Observability helper tests., setup_function() (+4 more)

### Community 38 - "Escalation Routes"
Cohesion: 0.07
Nodes (23): MemoryTool, Memory business logic — called by MCP server only (Week 13 pattern)., Up to ``k`` recent (user, assistant) pairs for this session., add_turn(), get_procedural(), _init(), tool, Memory MCP Server — exposes ST recall / add_turn / procedural lookup.  Adapted f (+15 more)

### Community 39 - "Chat Message Pipeline 2"
Cohesion: 0.18
Nodes (12): _get_bool(), get_chat_model(), get_embedding_model(), _get_nested(), get_role_config(), _get_str(), _load_yaml(), Any (+4 more)

### Community 40 - "Invoice DB Layer 2"
Cohesion: 0.21
Nodes (39): ChatChannel, EnrollmentStatus, EscalationStatus, ClassAnalyticsComparisonResponse, ClassAnalyticsMetric, ClassBase, ClassCreate, ClassHumanModeUpdate (+31 more)

### Community 41 - "Chat Message Pipeline 3"
Cohesion: 0.16
Nodes (18): main(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), preload_agent_runtime(), Any, Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., Store warmed instances from FastAPI lifespan (BookMe AI ``main.py`` pattern). (+10 more)

### Community 42 - "Dashboard ORM Models 2"
Cohesion: 0.25
Nodes (16): _ingest_result(), _minimal_docx(), _post(), patch, Multi-format ingest upload endpoint tests., test_delete_ingest_document(), test_get_ingest_document(), test_ingest_upload_docx() (+8 more)

### Community 43 - "Decision Graph 2"
Cohesion: 0.14
Nodes (13): IdentityContext, Resolved tenant + student scope for one WhatsApp conversation., Resolved tenant scope; student_id is set only when a DB record exists., Stable recall key — student id when enrolled, otherwise phone., Past papers and RAG require pending or active enrollment., format_student_profile(), Build recall context (student profile + ST turns) before the decision graph., Structured student block for router and agent prompts. (+5 more)

### Community 44 - "Escalation Routes 2"
Cohesion: 0.11
Nodes (19): Architecture, Dashboard overview & chat logs, Dev Chat — WhatsApp Simulator (No Twilio Required), Endpoints, Escalations (payment + talk-to-tutor), Fetch conversation history, Flow 1 — Payment receipt → dashboard inbox, Flow 2 — Talk to tutor (+11 more)

### Community 45 - "Dashboard Module"
Cohesion: 0.10
Nodes (35): BroadcastAudience, BroadcastFailure, BroadcastRecipient, BroadcastResult, class_display_name(), ClassNotFoundError, _fetch_students(), _fetch_telegram_channels() (+27 more)

### Community 19 - "API Chat Schemas"
Cohesion: 0.05
Nodes (40): chart.js, dependencies, chart.js, framer-motion, lucide-react, next, react, react-chartjs-2 (+32 more)

### Community 20 - "Design Double Diamond 3"
Cohesion: 0.09
Nodes (38): detect_script_language(), language_policy_block(), _latin_tokens(), looks_like_singlish(), looks_like_tanglish(), normalize_language_pref(), Reply-language resolution for Sinhala, Tamil, English, and code-switching.  Nati, Return si/ta when native script is present; None for Latin-only text. (+30 more)

### Community 47 - "CRM MCP Server"
Cohesion: 0.10
Nodes (38): build_direct_system_prompt(), build_escalation_ack_reply(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply(), build_resource_drive_list_reply(), build_resource_drive_pick_reply() (+30 more)

### Community 22 - "Dashboard ORM Models"
Cohesion: 0.08
Nodes (33): ClassesPage(), FaqsPage(), IngestContent(), OverviewPage(), DAYS, initialForm, ScheduleFormState, SchedulesPage() (+25 more)

### Community 50 - "Langfuse Runtime 2"
Cohesion: 0.08
Nodes (36): _remember_if_confirmation_asked(), classify_confirmation(), get_pending_low_confidence_question(), is_confirmation_prompt(), The academic question waiting on a yes/no tutor-handoff, if any.      Prefers th, True when the assistant just asked whether to send the question to the tutor., clear_pending_question(), peek_pending_question() (+28 more)

### Community 51 - "Test Suite"
Cohesion: 0.07
Nodes (34): _chain_mock(), main(), get_broadcast_recipients(), post_class_broadcast(), DashboardTenant, get, Staff class broadcast to Telegram-linked students., Preview who would receive a Telegram class announcement. (+26 more)

### Community 52 - "Agent Orchestrator 3"
Cohesion: 0.12
Nodes (16): Acceptance criteria mapping, Explicitly out of scope (stay V2), Handoff checklist (dashboard team), Makefile targets (to add), Phase 6 — Implementation Plan, Risk register, Starting point (what’s already done), Suggested schedule (1 day) (+8 more)

### Community 53 - "Admissions Onboarding 11"
Cohesion: 0.09
Nodes (28): Path, Measure how many real student messages still need an LLM round trip., read_cells(), aheuristic_route(), decision_from_intent(), _fallback_multi(), get_query_router(), heuristic_route() (+20 more)

### Community 54 - "Workshop Exploration"
Cohesion: 0.23
Nodes (15): _enrich_escalations(), EscalationActionResponse, list_escalations(), notify_student(), Any, BaseModel, DashboardTenant, get (+7 more)

### Community 55 - "Admissions Onboarding 12"
Cohesion: 0.12
Nodes (20): ClassesPage(), FaqsPage(), DAYS, initialForm, ScheduleFormState, SchedulesPage(), ChatTurn, DashboardAgentChat() (+12 more)

### Community 56 - "Supabase DB Client 2"
Cohesion: 0.13
Nodes (15): 10. Troubleshooting, 1. Prerequisites, 2. Clone and virtualenv, 3. Environment (`.env`), 4. Database, 5. Langfuse prompts, 6. RAG ingest (optional), 7. Run the API (+7 more)

### Community 57 - "Langfuse Runtime 3"
Cohesion: 0.16
Nodes (16): Base, Represents a tuition class offered by a tenant., SubjectClass, create_class(), delete_class(), get_class(), get_classes(), _parse_fee_cycle() (+8 more)

### Community 58 - "Decision Graph 3"
Cohesion: 0.14
Nodes (26): clear_bot_token_cache(), _fetch_tenant_bot_row(), get_bot_token_for_tenant(), get_telegram_bot_display_name(), Any, ValueError, Per-tenant Telegram bot token lookup (SRS NFR-17 — not env vars)., Raised when a tenant has no usable Telegram bot token. (+18 more)

### Community 59 - "Test Suite 2"
Cohesion: 0.10
Nodes (33): detect_script_language(), _latin_tokens(), looks_like_singlish(), looks_like_tanglish(), Reply-language resolution for Sinhala, Tamil, English, and code-switching.  Nati, Return si/ta when native script is present; None for Latin-only text., Script of this message wins; otherwise stored preference; otherwise English., True for romanized Sinhala mix (Singlish), not native Sinhala script. (+25 more)

### Community 60 - "Student Chat Deps 4"
Cohesion: 0.20
Nodes (8): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Support Langfuse `{{var}}` and local `{var}` placeholders., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 61 - "Workshop Exploration 2"
Cohesion: 0.16
Nodes (10): ExtractionError, normalize_markdown(), ValueError, Shared types for document extraction.  Every extractor converts source bytes int, Clean up extractor output so headings are usable as breadcrumbs.      Layout-der, Raised when a document cannot be turned into usable markdown.      Subclasses Va, extract_markdown(), Markdown / plain-text passthrough. (+2 more)

### Community 24 - "Agent Orchestrator"
Cohesion: 0.13
Nodes (11): column_available(), get_supabase_client(), list_tenants(), ping_supabase(), Any, Supabase REST client wrapper., Return a singleton Supabase client (requires service role key)., Lightweight connectivity check via tenants table. (+3 more)

### Community 25 - "Admissions Onboarding 8"
Cohesion: 0.09
Nodes (32): ClassReference, _closest(), extract_grade(), extract_subject(), _match_by_class_name(), Any, Entity extraction over real tenant data, with typo tolerance.  Students write "p, Return ``(subject, corrected_from)`` for the subject named in ``message``. (+24 more)

### Community 26 - "Drive Tooling 2"
Cohesion: 0.07
Nodes (30): get_broadcast_recipients(), post_class_broadcast(), DashboardTenant, get, Staff class broadcast to Telegram-linked students., Preview who would receive a Telegram class announcement., Send a class announcement to Telegram-linked enrolled students., get_chat_logs() (+22 more)

### Community 27 - "Supabase DB Client"
Cohesion: 0.10
Nodes (37): qdrant_collection_for_tenant(), collection_exists(), count_points(), delete_chunks_by_document_id(), delete_collection(), _dummy_vector(), ensure_class_id_index(), ensure_collection() (+29 more)

### Community 28 - "Agent Orchestrator 2"
Cohesion: 0.10
Nodes (29): formatReasonLabel(), InboxContent(), isPaymentReason(), statusClass(), MessagesContent(), senderBubbleClass(), EscalationSocketEvent, EscalationSocketEventType (+21 more)

### Community 29 - "Drive Tooling 3"
Cohesion: 0.11
Nodes (31): _last_user_text(), build_direct_system_prompt(), build_escalation_ack_reply(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply(), build_resource_drive_list_reply(), build_resource_drive_pick_reply() (+23 more)

### Community 30 - "Identity Context"
Cohesion: 0.12
Nodes (21): build_router_prompt(), aheuristic_route(), decision_from_intent(), _fallback_multi(), get_query_router(), heuristic_route(), _last_user_text(), MultiRouteDecision (+13 more)

### Community 31 - "Admissions Onboarding 9"
Cohesion: 0.12
Nodes (32): OnboardingFlow, Determine onboarding progress and extract slots from user messages., _assert_collection_restarted(), _awaiting_confirmation_state(), Onboarding flow unit tests., test_awaiting_review_state(), test_class_catalog_request_on_class_step(), test_class_disambiguation_for_physics() (+24 more)

### Community 32 - "Admissions Onboarding 10"
Cohesion: 0.06
Nodes (33): Agent pipeline, Axiom AI Backend — Finalize Checklist, Bot & environment, Core agent & routing, Dashboard handoff, Demo UI (`demo-ui-org/`), Documentation, Documentation sync (+25 more)

### Community 33 - "Resource Agent"
Cohesion: 0.14
Nodes (30): assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get_tenant_escalation_or_404(), Escalation, get, put (+22 more)

### Community 34 - "Chat Message Pipeline"
Cohesion: 0.12
Nodes (18): main(), main(), _one_turn(), get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session., session_id_for_phone() (+10 more)

### Community 35 - "Invoice DB Layer"
Cohesion: 0.10
Nodes (25): main(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), preload_agent_runtime(), Any, Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., Store warmed instances from FastAPI lifespan (BookMe AI ``main.py`` pattern). (+17 more)

### Community 36 - "Design Double Diamond 4"
Cohesion: 0.12
Nodes (31): commit_onboarding(), create_enrollment(), create_escalation(), get_class_details(), get_student(), get_tenant_info(), _init(), list_classes() (+23 more)

### Community 37 - "RAG Ingest Pipeline 5"
Cohesion: 0.18
Nodes (23): get_onboarding_session_store(), clear_onboarding_sessions(), FakeCrmClient, asyncio, fixture, Admissions agent node tests (in-process CRM, no MCP subprocess)., _state(), test_admissions_agent_asks_custom_field_instead_of_school() (+15 more)

### Community 38 - "Escalation Routes"
Cohesion: 0.08
Nodes (25): ChatResult, _is_slip_candidate(), _noop_emit(), Any, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, Remind the student of the flow their message interrupted.      Interrupting a fl, Whether an attachment should be routed to payment verification.      An unclassi, _remember_if_confirmation_asked() (+17 more)

### Community 39 - "Chat Message Pipeline 2"
Cohesion: 0.12
Nodes (29): _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_chat_turns(), get_conversation_thread(), get_thread_alias(), build_conversation_summary(), phone_from_session_id() (+21 more)

### Community 40 - "Invoice DB Layer 2"
Cohesion: 0.16
Nodes (28): get_class_analytics(), get_dashboard_analytics(), get_dashboard_chat_logs(), get_dashboard_escalations(), get_overview(), get_summary(), get, patch (+20 more)

### Community 41 - "Chat Message Pipeline 3"
Cohesion: 0.07
Nodes (29): compilerOptions, allowJs, baseUrl, esModuleInterop, incremental, isolatedModules, jsx, lib (+21 more)

### Community 65 - "Test Suite 3"
Cohesion: 0.13
Nodes (14): _client(), _noop_typing(), asyncio, _Query, Dashboard Agent identity, tenant isolation, and webhook split tests., test_agent_query_uses_jwt_tenant_not_query_param(), test_consume_link_code_is_tenant_scoped(), test_dashboard_agent_rejects_mismatched_tool_tenant() (+6 more)

### Community 66 - "IdentityResolver"
Cohesion: 0.08
Nodes (31): EscalationAgent, EscalationAgentResult, _last_user_text(), Escalation agent — talk-to-tutor requests → dashboard inbox., run_escalation_agent(), _last_user_text(), PaymentAgentResult, Payment Check agent — payment receipt → escalation inbox. (+23 more)

### Community 67 - "Chat Message Pipeline 4"
Cohesion: 0.28
Nodes (4): _build_class_analytics(), DashboardQueryTool, Any, test_dashboard_tool_rejects_empty_tenant()

### Community 68 - "Chat Turn Runner"
Cohesion: 0.09
Nodes (36): Enrollment, Base, Represents a student's enrollment in a subject class., Base, Represents a student registered under a tenant., Student, create_student(), delete_student() (+28 more)

### Community 69 - "Langfuse Runtime 4"
Cohesion: 0.12
Nodes (17): main(), main(), _one_turn(), main(), session_id_for_phone(), build_session_id(), IdentityResolver, normalize_phone() (+9 more)

### Community 70 - "MCP Integration"
Cohesion: 0.19
Nodes (11): PageText, One page of a paginated source document., _assemble(), extract_pdf(), _page_lacks_text(), _page_marker(), PDF → markdown via pymupdf4llm (text layer only — no vision OCR)., True when a page's text layer yielded too little to be real content. (+3 more)

### Community 71 - "Dashboard API Routes"
Cohesion: 0.13
Nodes (25): ResourceAgent, FakeDrive, FakeMemoryTool, FakeRag, asyncio, Identity recall and resource enrollment gate tests., test_build_recall_context_includes_profile_before_st(), test_identity_resolver_treats_unenrolled_row_as_visitor() (+17 more)

### Community 72 - "Escalation Routes 4"
Cohesion: 0.14
Nodes (30): assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get_tenant_escalation_or_404(), Escalation, get, put (+22 more)

### Community 46 - "Invoice DB Layer 3"
Cohesion: 0.13
Nodes (26): Enum, str, Canonical student intents and their mapping onto agent routes., What the student is actually asking for on this turn., StudentIntent, contains_abuse(), normalize_for_abuse(), Abuse detection that does not depend on sentence structure.  "Why do you suck so (+18 more)

### Community 47 - "CRM MCP Server"
Cohesion: 0.14
Nodes (22): emptyForm(), FALLBACK_DISTRICT_FIELD, matchesStudentSearch(), ModalMode, StudentsPage(), EnrollModal(), EnrollModalProps, extraFieldsFromStudent() (+14 more)

### Community 48 - "Escalation Routes 3"
Cohesion: 0.07
Nodes (28): 🤖 Agent Pipeline, AI Backend (`:8000`), 📡 API Reference, Axiom AI, Backend, Backend (AI Agents & MCP), 🔄 CI/CD Pipeline, ⚙️ Configuration (+20 more)

### Community 49 - "Langfuse Runtime"
Cohesion: 0.13
Nodes (25): _list_children(), main(), _mask_path(), _print_summary(), TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).  Does not, step10b_mcp(), step12_network(), step1_environment() (+17 more)

### Community 74 - "ShortTermMemoryStore"
Cohesion: 0.31
Nodes (6): PaymentAgent, FakeCrm, asyncio, Payment Check agent tests., test_payment_agent_creates_escalation_with_media(), test_payment_agent_requires_media()

### Community 75 - "Dashboard Module 2"
Cohesion: 0.14
Nodes (13): _format_citation_label(), format_docs(), RAG helper utilities., Format LangChain documents into a single context block., build_rag_chain(), Config, Any, Plain RAG service — Qdrant retrieval + Gemini synthesis (no CAG/CRAG). (+5 more)

### Community 76 - "Admissions Onboarding 13"
Cohesion: 0.17
Nodes (12): Acceptance criteria mapping, Agent ownership, Core decision: escalation-only HITL, Dashboard API (implemented), Decisions explicitly skipped, Flow 1 — Payment receipt, Flow 2 — Talk to tutor, Phase 5 — Design Decisions (As Implemented) (+4 more)

### Community 77 - "infrastructure config py"
Cohesion: 0.17
Nodes (12): 16.10 V2 Architecture Upgrades (Reference Patterns), 16.11 V2 Acceptance Themes, 16.1 Messaging & Infrastructure, 16.2 AI Agents & Orchestration, 16.3 Memory, Caching & RAG Enhancements, 16.4 Payments & Finance Automation, 16.5 Integrations & Tooling, 16.6 CRM, Dashboard & Backend APIs (Extended) (+4 more)

### Community 78 - "Langfuse Runtime 5"
Cohesion: 0.21
Nodes (13): download_telegram_file(), get_telegram_file_path(), _keep_telegram_typing(), Response, _raise_telegram_error(), Thin Telegram Bot API client — one token per tenant, never a global token., Resolve a Telegram file_id to a downloadable file_path via getFile., Download the raw bytes of a Telegram file (image or voice note). (+5 more)

### Community 79 - "Admissions Onboarding 14"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 80 - "test_identity_recall.py"
Cohesion: 0.13
Nodes (14): classify_resource_subpath(), _folder_from_route_params(), _infer_drive_folder(), _last_user_text(), Keyword sub-router: schedule > drive (file folders) > rag., Map a file request to papers, textbooks, or syllabus., Handle Drive file requests., Handle RAG knowledge base queries. (+6 more)

### Community 81 - "_tracing_enabled"
Cohesion: 0.13
Nodes (26): _disable_langfuse(), flush(), get_current_trace_id(), get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), langfuse_turn_attributes() (+18 more)

### Community 82 - "Escalation Routes 6"
Cohesion: 0.18
Nodes (7): chat_result(), client(), asyncio, fixture, HTTP dev chat endpoint tests., Regression: /chat must not call asyncio.run() inside FastAPI's event loop., test_chat_pipeline_runs_agent_inside_event_loop()

### Community 83 - "Escalation Routes 7"
Cohesion: 0.05
Nodes (35): get_day_of_week(), get_tenant_now(), get_tenant_timezone(), get_tenant_today(), datetime, Schedule service — timetable CRUD, queries, and centralized timezone handling., Fetch tenant timezone from DB. Returns default if not set., Get all active schedules for a specific date, with exceptions applied. (+27 more)

### Community 84 - "Drive Tooling 4"
Cohesion: 0.11
Nodes (29): _closest(), extract_grade(), extract_subject(), _match_by_class_name(), Any, Entity extraction over real tenant data, with typo tolerance.  Students write "p, Return ``(subject, corrected_from)`` for the subject named in ``message``., Resolve a class mention against the tenant's real class rows.      Both the subj (+21 more)

### Community 85 - "Resource Agent 2"
Cohesion: 0.06
Nodes (19): mock_client(), MockSupabaseClient, MockSupabaseResponse, MockSupabaseTable, asyncio, fixture, Tests for schedule CRUD, recurring schedules, exceptions, timezone, and multiple, Mock Supabase client for unit tests. (+11 more)

### Community 86 - "Dashboard Module 3"
Cohesion: 0.15
Nodes (15): emptyForm, StaffFormState, StaffPage(), ToastContainer(), toastStyles(), Toast, ToastContext, ToastContextValue (+7 more)

### Community 87 - "Dashboard API Routes 2"
Cohesion: 0.17
Nodes (17): ChatChannel, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, MessageRole, PaymentStatus, Enum (+9 more)

### Community 51 - "Test Suite"
Cohesion: 0.13
Nodes (23): Enrollment, Base, Represents a student's enrollment in a subject class., Base, Represents a student registered under a tenant., Student, create_student(), delete_student() (+15 more)

### Community 52 - "Agent Orchestrator 3"
Cohesion: 0.12
Nodes (19): Base, Per-tenant custom onboarding field (beyond name/phone/class/consent)., TenantFieldDefinition, OnboardingFieldInput, FieldConfigLockedError, Session, ValueError, Persist and lock per-tenant onboarding field definitions. (+11 more)

### Community 90 - "Test Suite 5"
Cohesion: 0.15
Nodes (8): OnboardingState, Multi-turn admissions onboarding — slot tracking and class disambiguation., Hydrate state for an existing database student (post-enrollment paths only)., OnboardingSession, OnboardingSessionStore, In-memory onboarding session store — Week 13 SessionStore pattern.  Onboarding s, Ephemeral multi-turn onboarding progress for one tenant+phone pair., Process-local store keyed by ``tenant_id:phone``.

### Community 91 - "Supabase DB Client 4"
Cohesion: 0.46
Nodes (3): Axiom AI — Multi-Agent Backend, Docs, Quick start

### Community 92 - "TwilioMessagingClient"
Cohesion: 0.23
Nodes (8): extract_docx(), _heading_level(), _looks_like_heading(), _promote_bold_headings(), DOCX → markdown via mammoth (HTML) → markdownify.  mammoth keys off Word's *sema, Turn standalone whole-line bold paragraphs into markdown headings., Extract markdown from .docx bytes., TestPromoteBoldHeadings

### Community 93 - "Escalation Routes 8"
Cohesion: 0.07
Nodes (42): bind_telegram_student_channel(), _delete_pending(), _has_enrollment(), link_telegram_contact(), _lookup_pending_phone(), _lookup_student_by_phone(), _parse_channel(), _pending_identity() (+34 more)

### Community 94 - "test_twilio_webhook.py"
Cohesion: 0.15
Nodes (13): `audit_logs` (AUDIT_LOG), `bank_slip_uploads` (BANK_SLIP_UPLOAD), `enrollments` (ENROLLMENT), `escalations` (ESCALATION), `invoices` (INVOICE), `message_logs` (MESSAGE_LOG), `parent_guardians` (PARENT_GUARDIAN), `staff_users` (STAFF_USER) (+5 more)

### Community 96 - "Dashboard Module 4"
Cohesion: 0.47
Nodes (9): _chat(), main(), _phone(), _require_live_env(), scenario_escalation(), scenario_onboarding(), scenario_out_of_scope(), scenario_payment() (+1 more)

### Community 97 - "Escalation Routes 11"
Cohesion: 0.14
Nodes (24): Enum, str, Canonical student intents and their mapping onto agent routes., What the student is actually asking for on this turn., StudentIntent, contains_abuse(), normalize_for_abuse(), Abuse detection that does not depend on sentence structure.  "Why do you suck so (+16 more)

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
Cohesion: 0.18
Nodes (13): analyze_tenant_faqs(), Any, DashboardTenant, FAQ intelligence endpoint for dashboard staff., Cluster recent student questions for one class into recurring FAQ themes., analyze_faqs(), _clean_message(), FAQCluster (+5 more)

### Community 105 - "Admissions Onboarding 18"
Cohesion: 0.10
Nodes (22): True when the message is a different request, not onboarding input., should_break_onboarding_lock(), aclassify(), _build_index(), classify(), _classify_uncached(), _copy_result(), Semantic intent classification for incoming student messages.  Three tiers, chea (+14 more)

### Community 106 - "Escalation Routes 13"
Cohesion: 0.25
Nodes (7): API Key Auth via Header, CORS Configuration, FastAPI OAuth2 Bearer Dependency, Hide OpenAPI Docs by Default, JWT Create/Verify (python-jose), Password Hashing (passlib + bcrypt), Security Patterns

### Community 107 - "Dashboard API Routes 3"
Cohesion: 0.25
Nodes (7): Build, Demo UI — WhatsApp Student Chat, Env (optional), Features, Prerequisites, Project layout, Quick start

### Community 108 - "MCP Integration 4"
Cohesion: 0.15
Nodes (23): handle_text_message(), client(), no_staff_on_webhook(), _noop_typing(), asyncio, fixture, Telegram webhook + ChatPipeline wiring tests., Student webhook tests must not hit staff_channels / link-code tables. (+15 more)

### Community 54 - "Workshop Exploration"
Cohesion: 0.12
Nodes (15): _client(), _noop_typing(), asyncio, _Query, Dashboard Agent identity, tenant isolation, and webhook split tests., test_agent_query_uses_jwt_tenant_not_query_param(), test_consume_link_code_is_tenant_scoped(), test_dashboard_agent_rejects_mismatched_tool_tenant() (+7 more)

### Community 55 - "Admissions Onboarding 12"
Cohesion: 0.08
Nodes (25): API Design, Async Routes, Async Test Client from Day 0, Chain Dependencies, CPU Intensive Tasks, Custom Base Model, Decouple BaseSettings, Dependencies (+17 more)

### Community 111 - "Test Suite 7"
Cohesion: 0.18
Nodes (16): ExtractedDoc, Normalized extraction result handed to the ingest pipeline., Synchronous upload ingest (used in tests and CLI).      Dashboard uploads use :f, Deprecated alias for :func:`run_upload_ingest`, kept for one release., run_pdf_ingest(), run_upload_ingest(), _fake_ingest_result(), _minimal_docx() (+8 more)

### Community 112 - "Dashboard Module 6"
Cohesion: 0.19
Nodes (22): _dispatch(), Any, looks_like_link_code(), Any, Send a message with a one-time 'Share phone number' keyboard., Send a plain text message to a Telegram chat using that tenant's bot token., send_telegram_contact_request(), send_telegram_message() (+14 more)

### Community 58 - "Decision Graph 3"
Cohesion: 0.08
Nodes (25): Dashboard API Contract (Phase 5), Document ingest (knowledge base), Endpoint map, Escalation inbox (unified HITL queue), Escalation object, Get thread (message panel), How to pass tenant, Integration flow (recommended) (+17 more)

### Community 59 - "Test Suite 2"
Cohesion: 0.11
Nodes (10): Memory business logic — called by MCP server only (Week 13 pattern)., ProceduralMemoryStore, Procedural memory store — tenant-scoped ``mem_procedures`` lookup.  Adapted from, ConversationTurn, Procedure, Memory schemas — ported from Week 13 ``memory/schemas.py`` (MVP subset)., Short-term memory store — Supabase ``st_turns`` ring buffer.  Adapted from Week, Return up to k most recent (user, assistant) pairs.          ``recall_turns`` is (+2 more)

### Community 116 - "Dashboard Module 7"
Cohesion: 0.09
Nodes (49): StaffRole, Base, Represents a staff member of a tuition institute., StaffUser, bootstrap_demo_physics(), create_telegram_link_code(), login(), me() (+41 more)

### Community 61 - "Workshop Exploration 2"
Cohesion: 0.09
Nodes (18): classify_media(), MediaKind, Enum, str, Classify an inbound attachment so each media type gets its own handling.  The in, Formats a bank slip plausibly arrives in., Best-effort media kind from a Content-Type header or URL extension., _suffix() (+10 more)

### Community 62 - "RAG Tooling"
Cohesion: 0.08
Nodes (23): Basic Setup, Batch Messages, Best Practices, FastAPI Caching, FastAPI Rate Limiting, FastAPI Session Management, Hash Operations, Key Expiration (TTL) (+15 more)

### Community 63 - "CRM MCP Server 2"
Cohesion: 0.08
Nodes (24): 1. Google Cloud, 2. Environment, Architecture, Folder ID, Folder layout, Google Drive MCP — Integration & Testing, Multi-tenant isolation, MVP vs v2 (+16 more)

### Community 121 - "MCP Integration 5"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Dependencies, Features, Files / Modules, Objective, Phase 2 — Agent Framework (Decision Graph + Chat Pipeline), Reference Implementation (copy — do not invent)

### Community 122 - "verify phase0 py"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Features, Files / Modules, Google Drive MVP Approach, Objective, Phase 4 — Resource Agent (Drive + RAG), Reference Implementation (copy — do not invent)

### Community 123 - "Resource Agent 3"
Cohesion: 0.20
Nodes (7): MessagePersistence, ChatChannel, MessageRole, Persist inbound/outbound messaging to Supabase (message_logs + st_turns)., Return the latest turn per session_id, ordered by most recent activity., Write message_logs and st_turns rows for a conversation turn., Persist a staff-authored message (role=system → sender=staff in dashboard UI).

### Community 124 - "Dashboard Frontend Deps 2"
Cohesion: 0.13
Nodes (22): main(), title_from_filename(), _attach_document_ids(), delete_document_ingest(), embed_texts(), ingest_documents(), load_tenant_docs(), prepare_upload_ingest() (+14 more)

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
Nodes (20): EmitFn, run_chat_turn(), RouteDecision, _mock_oos_graph(), asyncio, Fast E2E wiring tests (mocked LLM — BookMe / Week 13 decision_graph test pattern, Minimal stand-in — records whether orchestrator path runs (BookMe AI pattern)., _RecordingOrchestrator (+12 more)

### Community 129 - "Student Chat Deps 7"
Cohesion: 0.16
Nodes (17): DriveTool, Business logic for drive_search / drive_list — used by drive_server and REST., _clear_drive_cache(), _load_physics(), mock_backend(), _nested_backend(), fixture, Drive tool unit tests — class-scoped nested Drive layout. (+9 more)

### Community 130 - "Decision Graph 4"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 131 - "Supabase DB Client 6"
Cohesion: 0.33
Nodes (6): 8.1 Agentic Workforce and Conversational Interface, 8.2 Financial and Ticket Management, 8.3 Administrative Dashboard and Agency CRM, 8.5 Marketing and Lead Management, 8.6 Platform Administration and Multi-Tenancy (New), 8\. Functional Requirements

### Community 132 - "P0 — Must finalize (MVP gate)"
Cohesion: 0.27
Nodes (8): Normalize student-facing chat text for WhatsApp and Telegram., Remove markdown ``**bold**`` markers so they do not show as raw asterisks., strip_markdown_markers(), Plain-text sanitizer for student-facing messages., test_empty_and_none_safe(), test_leaves_plain_text_unchanged(), test_strips_bold_markers(), test_strips_multiple_bold_spans()

### Community 133 - "preload agent runtime"
Cohesion: 0.29
Nodes (9): _parse_form_params(), BackgroundTasks, Request, Response, Twilio WhatsApp webhook router., Twilio WhatsApp sandbox webhook.      Returns 200 immediately and processes the, _should_validate_signature(), twilio_webhook() (+1 more)

### Community 134 - "page_needs_ocr"
Cohesion: 0.18
Nodes (11): main(), Send a student message and receive an AI reply.      Use this during development, send_chat_message(), ChatPipeline, Reply for an attachment we can't pass on, or ``None`` to keep going.          A, Channel-agnostic chat pipeline — HTTP dev chat + Twilio webhook., Sync entry for scripts and tests without a running event loop., InboundMessage (+3 more)

### Community 135 - "test_run_resource_agent_requires_mcp_clients_when_fallback_disabled"
Cohesion: 0.36
Nodes (7): _init(), kb_ingest_status(), kb_search(), tool, RAG MCP Server — tenant-scoped tutor-note Q&A., Search tutor lesson notes (Qdrant) and return a grounded answer with citations., Return Qdrant ingest status for a tenant's tutor-note collection.

### Community 136 - "Dashboard Frontend Deps 3"
Cohesion: 0.26
Nodes (8): FakeDrive, Any, asyncio, Class-scoped RAG retrieval tests., test_kb_search_forwards_class_ids_to_rag_service(), test_resource_agent_blocks_enrolled_without_class_ids(), test_resource_agent_passes_enrolled_class_ids_to_rag(), TrackingRag

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
Cohesion: 0.22
Nodes (13): TenantStatus, Base, Represents a tuition institute (tenant) in the Axiom AI platform.     Every busi, Tenant, get_onboarding_fields(), get_tenant_profile(), list_tenants(), _normalize_slug() (+5 more)

### Community 144 - "kb_documents.py"
Cohesion: 0.40
Nodes (9): delete_document(), get_document(), list_documents(), mark_failed(), _now_iso(), Any, Supabase registry for ingested tutor documents., registry_available() (+1 more)

### Community 145 - "Demo UI"
Cohesion: 0.33
Nodes (16): Best-effort chat action (typing). Failures are logged, never raised., send_telegram_chat_action(), telegram_api_url(), _async_client(), _json_response(), asyncio, Telegram Bot API client tests — tenant token isolation., test_download_telegram_file_uses_matching_token() (+8 more)

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
Cohesion: 0.31
Nodes (8): active_config(), health(), get, Request, Health, readiness, and config endpoints., ready(), langfuse_configured(), HealthResponse

### Community 152 - "Phase 5 — Escalations + staff chat"
Cohesion: 0.21
Nodes (13): consume_staff_link_code(), normalize_link_code(), _parse_channel(), _parse_dt(), Any, ChatChannel, datetime, Resolve staff from a channel address (e.g. Telegram chat_id) and consume link co (+5 more)

### Community 66 - "IdentityResolver"
Cohesion: 0.09
Nodes (22): Alembic Migration Naming, Async Engine + Session, Bulk Insert, Bulk Operations, Bulk Update, Cascade Delete, Commit/Rollback Pattern, Constraint Naming (+14 more)

### Community 67 - "Chat Message Pipeline 4"
Cohesion: 0.09
Nodes (23): Application Access Patterns, Apply schema, Axiom AI — Database Documentation, Demo Seed Data, ENUM Types, ER Diagram, ER entity → SQL table mapping, Legacy v1 Tables (removed) (+15 more)

### Community 68 - "Chat Turn Runner"
Cohesion: 0.09
Nodes (22): 10. Technical decisions, 11. Risks & mitigations, 12. Acceptance criteria, 13. Future (post-hackathon), 1. Product concept, 2. Folder structure, 3. BookMe AI → Axiom file mapping, 4. API integration (student chat) (+14 more)

### Community 69 - "Langfuse Runtime 4"
Cohesion: 0.09
Nodes (22): 10. Deferred to Phase 3+, 1. Where we are today, 2. Binding constraint: no torch in the runtime image, 3. Target architecture, 4. Chunking upgrade, 5. Phase 1 — extraction router, 6. Phase 2 — correctness and lifecycle, 7. Configuration (+14 more)

### Community 70 - "MCP Integration"
Cohesion: 0.17
Nodes (21): _dispatch(), Any, looks_like_link_code(), _contact_prompt(), _display_name(), handle_contact_shared(), handle_photo_message(), handle_staff_text_message() (+13 more)

### Community 158 - "Admissions Onboarding 20"
Cohesion: 0.19
Nodes (10): column_available(), is_undefined_column_error(), mark_column_missing(), BaseException, Tolerate schema lag when optional columns are not yet migrated., reset_missing_columns(), Schema compatibility helpers for optional DB columns., setup_function() (+2 more)

### Community 72 - "Escalation Routes 4"
Cohesion: 0.14
Nodes (14): CrmTool, mock_db(), fixture, CRM tool and tenant isolation tests., test_commit_onboarding_completes_unenrolled_profile(), test_commit_onboarding_rejects_already_enrolled(), test_commit_onboarding_writes_extra_fields(), test_create_enrollment_rejects_cross_tenant_class() (+6 more)

### Community 178 - ".create_escalation"
Cohesion: 0.17
Nodes (10): Any, Atomic post-confirmation write: student profile + pending enrollment., Update student profile fields for onboarding., coerce_extra_fields(), merge_column_backed_fields(), Any, Tenant onboarding field definitions — custom slots beyond core name/class/consen, Dual-write school/district into extra_fields; copy extra keys into columns. (+2 more)

### Community 214 - "RateLimitMiddleware"
Cohesion: 0.16
Nodes (19): Message shapes whose meaning does not depend on wording., _structural_intent(), canonical_tokens(), closest_term(), contains_url(), has_word_characters(), is_emoji(), looks_like_request() (+11 more)

### Community 74 - "ShortTermMemoryStore"
Cohesion: 0.12
Nodes (18): aclassify(), _build_index(), classify(), _classify_uncached(), _copy_result(), Semantic intent classification for incoming student messages.  Three tiers, chea, Domain vocabulary used for typo correction., IDF-weighted F1 between the message and each intent's best example.      Recall (+10 more)

### Community 216 - "PaymentStatusUpdate"
Cohesion: 0.15
Nodes (13): HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required)., FeeCycle, InvoiceStatus, Enum, str, Domain status enums — mirror PostgreSQL ENUM types in sql/01_schema.sql., StaffRole, Domain types — enums and value objects. (+5 more)

### Community 217 - "FakeCrm"
Cohesion: 0.27
Nodes (6): extract_document(), max_upload_bytes(), SourceType, Multi-format document extraction — PDF, DOCX and Markdown to markdown.  Every ex, Sniff the format of ``content`` and extract it to markdown.      Raises Extracti, TestExtractDocument

### Community 218 - "Testing"
Cohesion: 0.32
Nodes (7): get_student(), Any, get, Student registration and lookup — dashboard + dev API., Register or update a student profile (dashboard / manual onboarding)., Fetch student profile and enrollments by phone., register_student()

### Community 219 - "telegram_webhook"
Cohesion: 0.17
Nodes (8): parse_twilio_form(), Parse Twilio application/x-www-form-urlencoded webhook bodies., test_twilio_form_carries_the_declared_content_type(), client(), identity_ctx(), fixture, Twilio webhook endpoint tests., test_parse_twilio_form_extracts_media()

### Community 220 - "register_student"
Cohesion: 0.24
Nodes (7): ClassAnalyticsPage(), formatClassTitle(), PERIOD_OPTIONS, SortKey, AnalyticsPeriod, ClassAnalyticsComparison, getClassAnalytics()

### Community 221 - "conftest.py"
Cohesion: 0.31
Nodes (4): BaseHTTPMiddleware, Request, Response, RateLimitMiddleware

### Community 223 - "seed_langfuse_prompts.py"
Cohesion: 0.25
Nodes (5): ABC, Abstract cache for idempotency. Implement get/set/delete for Redis/DB., Return cached transcript, or None if miss/expired., Store value with TTL in seconds. value=None means 'in-progress'., SttCache

### Community 225 - "smoke_mcp_memory.py"
Cohesion: 0.33
Nodes (5): list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant.

### Community 226 - "8. Implementation phases"
Cohesion: 0.48
Nodes (6): _llm_content_to_str(), Any, Staff dashboard Q&A agent — separate from the student Guardrail/Router/Orchestra, Answer a staff dashboard question. tenant_id is taken only from ``staff``., run_dashboard_agent(), _select_context()

### Community 227 - "decision_bridge.py"
Cohesion: 0.08
Nodes (37): main(), _primary_route(), RoutingCase, _run(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, build_decision_graph(), build_decision_input() (+29 more)

### Community 228 - "agent.py"
Cohesion: 0.43
Nodes (6): dashboard_agent_query(), DashboardAgentQueryRequest, DashboardAgentQueryResponse, BaseModel, Authenticated staff dashboard Q&A — JWT only, tenant from staff row., StaffPrincipal

### Community 229 - ".resolve_escalation"
Cohesion: 0.15
Nodes (18): delete_document(), get_document(), list_documents(), BackgroundTasks, DashboardTenant, delete, get, UploadFile (+10 more)

### Community 88 - "MCP Integration 2"
Cohesion: 0.17
Nodes (10): _looks_like_text(), SourceType, Detect upload format from content, not from the filename.  Both the filename and, Heuristic: decodable as UTF-8 and free of NUL bytes., Return the source type for ``content``, or raise ExtractionError.      ``filenam, sniff_format(), _zip_format(), _ooxml() (+2 more)

### Community 89 - "Test Suite 4"
Cohesion: 0.26
Nodes (18): clear_sessions(), _enrolled_student(), _is_payment_prompt(), asyncio, fixture, parametrize, End-to-end admissions regressions from the student-side QA log.  Category B is t, _staff_stub() (+10 more)

### Community 90 - "Test Suite 5"
Cohesion: 0.13
Nodes (15): get_db(), _load_env(), Load env from Dashboard, shared AI-backend, or repo root., get_tenant_id(), Authenticated tenant scope for dashboard API requests., create_message_log(), get_message_logs(), get (+7 more)

### Community 91 - "Supabase DB Client 4"
Cohesion: 0.13
Nodes (14): classify_resource_subpath(), _folder_from_route_params(), _infer_drive_folder(), _last_user_text(), Keyword sub-router: schedule > drive (file folders) > rag., Map a file request to papers, textbooks, or syllabus., Handle Drive file requests., Handle RAG knowledge base queries. (+6 more)

### Community 92 - "TwilioMessagingClient"
Cohesion: 0.14
Nodes (9): DriveClient, Protocol, RagClient, Protocol for schedule lookups — Direct or MCP., run_resource_agent(), ScheduleClient, asyncio, Resource agent — in-process tools blocked when ALLOW_INPROCESS_TOOLS=false. (+1 more)

### Community 93 - "Escalation Routes 8"
Cohesion: 0.17
Nodes (8): _doc(), Markdown-aware chunking: heading sections, breadcrumbs, page attribution., Real token counting, not the old chars/4 approximation., A verbose H1 must not crowd out the specific heading on every chunk., test_token_len_beats_char_estimate(), TestChunkContract, TestHeadingSections, TestPageAttribution

### Community 94 - "test_twilio_webhook.py"
Cohesion: 0.25
Nodes (16): _ingest_result(), _minimal_docx(), _post(), patch, Multi-format ingest upload endpoint tests., test_delete_ingest_document(), test_get_ingest_document(), test_ingest_upload_docx() (+8 more)

### Community 95 - "Escalation Routes 10"
Cohesion: 0.29
Nodes (16): demo_login(), login(), Public hackathon shortcut — ensures demo admin exists, then signs in., register(), AuthResponse, AuthUserResponse, CreatedStaffResponse, LoginRequest (+8 more)

### Community 233 - "log.py"
Cohesion: 0.09
Nodes (24): get_db(), _load_env(), Load env from Dashboard, shared AI-backend, or repo root., get_current_staff(), HTTPAuthorizationCredentials, Session, get_tenant_id(), Authenticated tenant scope for dashboard API requests. (+16 more)

### Community 234 - "admissions_db_client.py"
Cohesion: 0.19
Nodes (13): decide_flow_action(), flow_kind_for_student(), FlowAction, FlowDecision, FlowKind, Enum, str, Per-turn decision: continue an in-progress flow, or interrupt it.  The old behav (+5 more)

### Community 235 - "Escalation inbox (unified HITL queue)"
Cohesion: 0.12
Nodes (15): 10. Known Sandbox Limitations to Flag (be upfront about these, don't get caught off guard), 1. Account Setup (15–30 min), 2. How the Flow Maps to Your Existing Architecture, 3. Install Dependencies, 4. Build the Webhook Endpoint, 5. Critical Constraint: The 3-Second Webhook Window, 6. Exposing Your Local Backend to Twilio (for testing before deployment), 7. Handling Voice Notes (ties into your P0 voice transcription feature) (+7 more)

### Community 236 - "test_merge_response.py"
Cohesion: 0.36
Nodes (7): drive_list(), drive_search(), _init(), tool, Drive MCP Server — papers, textbooks, syllabus only., Search class-scoped Drive folders (papers, textbooks, syllabus). Requires enroll, List files in an allowed class Drive subfolder (papers, textbooks, syllabus).

### Community 237 - "_emit_from_config"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features *(original plan — see PHASE5_DECISIONS.md for what changed)*, Files / Modules, Objective, Phase 5 — Payment Check, Escalation & Dashboard APIs, Reference Implementation (copy — do not invent)

### Community 238 - "test_health.py"
Cohesion: 0.25
Nodes (3): client(), fixture, Phase 0 health endpoint tests.

### Community 239 - "escalation_reasons.py"
Cohesion: 0.40
Nodes (4): _InterceptHandler, Centralised loguru setup (stderr-only for future MCP safety)., setup_logging(), LogRecord

### Community 240 - "send_chat_message"
Cohesion: 0.40
Nodes (5): _call_gemini(), _is_retryable(), Exception, Check if an exception is transient and worth retrying., Send voice note to Gemini for transcription with retry.

### Community 241 - "get_current_staff"
Cohesion: 0.40
Nodes (4): _content_type_supported(), _download_with_retry(), Check if the Content-Type header indicates a voice note (OGG Opus)., Download voice note from a URL with retry and Content-Type validation.      If a

### Community 242 - "supabase_client.py"
Cohesion: 0.33
Nodes (5): list_tenants(), ping_supabase(), Any, Supabase REST client wrapper., Lightweight connectivity check via tenants table.

### Community 244 - ".list_recent_sessions"
Cohesion: 0.67
Nodes (3): get_stt_metrics(), Any, Return current transcription metrics. Call from a /metrics endpoint.

### Community 245 - "smoke_resource.py"
Cohesion: 0.20
Nodes (13): get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session., build_conversation_summary(), phone_from_session_id(), Any, MessageRole (+5 more)

### Community 246 - ".kb_search"
Cohesion: 0.33
Nodes (3): CRM business logic — called by MCP server only (Week 13 pattern)., Escalation reason codes for dashboard inbox filtering., Supabase access for admissions CRM operations.

### Community 247 - "utils.py"
Cohesion: 0.27
Nodes (13): decide(), parametrize, Regression tests for sticky flow-state (category B in the QA log).  The reported, A typed slot value shares vocabulary with real intents; shape decides., test_b1_b3_new_requests_interrupt_a_pending_payment(), test_b5_shared_link_interrupts_every_flow(), test_conversational_replies_continue_the_flow(), test_enrollment_talk_continues_onboarding_but_interrupts_payment() (+5 more)

### Community 248 - "field_definitions.py"
Cohesion: 0.18
Nodes (10): ErrorRag, FakeDrive, asyncio, User-facing resource agent reply error sanitization., test_build_resource_drive_list_reply_omits_links(), test_build_resource_drive_list_reply_tags_union_classes(), test_build_resource_drive_reply_hides_internal_error(), test_build_resource_rag_reply_hides_internal_error() (+2 more)

### Community 249 - "seed_langfuse_prompts.py"
Cohesion: 0.25
Nodes (5): Validate config and ensure data directories exist., validate(), Config and tenant isolation unit tests., test_qdrant_collection_per_tenant(), test_validate_creates_directories()

### Community 250 - "test_heuristic_router.py"
Cohesion: 0.60
Nodes (4): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog()

### Community 251 - "send_chat_message"
Cohesion: 0.38
Nodes (6): get_drive_tool(), get_rag_tool(), get_request_id(), Request, FastAPI dependency injection helpers., _require_startup()

### Community 252 - ".list_recent_sessions"
Cohesion: 0.28
Nodes (6): _class_mentioned(), _class_name_candidates(), _normalize_drive_folder_id(), Any, Drive tool — class-scoped paper/textbook/syllabus search under a tenant root., Strip URL query junk users paste from Drive share links (e.g. ``?usp=drive_link`

### Community 102 - "Test Suite 6"
Cohesion: 0.20
Nodes (7): MessagePersistence, ChatChannel, MessageRole, Persist inbound/outbound messaging to Supabase (message_logs + st_turns)., Return the latest turn per session_id, ordered by most recent activity., Write message_logs and st_turns rows for a conversation turn., Persist a staff-authored message (role=system → sender=staff in dashboard UI).

### Community 103 - "Admissions Onboarding 17"
Cohesion: 0.20
Nodes (8): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Support Langfuse `{{var}}` and local `{var}` placeholders., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 104 - "MCP Integration 3"
Cohesion: 0.21
Nodes (13): Base, Represents a tuition institute (tenant) in the Axiom AI platform.     Every busi, Tenant, bootstrap_demo_physics(), authenticate_staff(), build_unique_slug(), ensure_demo_physics_staff(), hash_password() (+5 more)

### Community 105 - "Admissions Onboarding 18"
Cohesion: 0.17
Nodes (12): DashboardLayoutProps, ProtectedDashboard(), Header(), HeaderProps, useAuth(), TenantProvider(), useTheme(), Toast (+4 more)

### Community 106 - "Escalation Routes 13"
Cohesion: 0.13
Nodes (15): 10. Troubleshooting, 1. Prerequisites, 2. Clone and virtualenv, 3. Environment (`.env`), 4. Database, 5. Langfuse prompts, 6. RAG ingest (optional), 7. Run the API (+7 more)

### Community 107 - "Dashboard API Routes 3"
Cohesion: 0.13
Nodes (15): 11. API Contract Summary (Dashboard Team), 12. Environment Variables, 13. Explicitly Out of MVP Scope, 14. Per-Phase Workflow, 15. Day-by-Day Schedule, 1. Locked Architecture Decisions, 6. Resource Split: Google Drive vs RAG, 9. High-Level Architecture (+7 more)

### Community 108 - "MCP Integration 4"
Cohesion: 0.19
Nodes (9): Any, Atomic post-confirmation write: student profile + pending enrollment., Update student profile fields for onboarding., coerce_extra_fields(), merge_column_backed_fields(), Any, Dual-write school/district into extra_fields; copy extra keys into columns., test_merge_copies_column_keys_from_extra_when_args_missing() (+1 more)

### Community 109 - "RAG Ingest Pipeline 6"
Cohesion: 0.19
Nodes (13): decide_flow_action(), flow_kind_for_student(), FlowAction, FlowDecision, FlowKind, Enum, str, Per-turn decision: continue an in-progress flow, or interrupt it.  The old behav (+5 more)

### Community 110 - "Supabase DB Client 5"
Cohesion: 0.17
Nodes (4): AdminRegistration, field_validator, StaffRegistration, EmailStr

### Community 111 - "Test Suite 7"
Cohesion: 0.21
Nodes (13): apply_student_extra_fields(), _flag_extra_fields(), _normalize_extra_value(), _optional_column_str(), Any, Keep extra_fields.school/district in sync without dropping other keys., Merge extra_fields and dual-write school/district columns., sync_column_backed_extra_fields() (+5 more)

### Community 112 - "Dashboard Module 6"
Cohesion: 0.14
Nodes (13): Async Routes, Core Principles, Dependency Injection, Project Structure, Pydantic Validation, python-backend, Quick Patterns, Rate Limiting (+5 more)

### Community 113 - "RAG Ingest Pipeline 7"
Cohesion: 0.14
Nodes (13): 10. Setup Checklist for Your Two-Tutor Pilot, 1. Why "One Bot Per Tutor/Institute" Is the Right Call, 2. Creating a Bot (per tutor/institute) — 2 Minutes Each, 3. Webhook Architecture — One Endpoint, Tenant Identified by URL Path, 4. Sending Responses Back, 5. Solving Your Core Requirement: Identifying the Student by Phone Number, 6. Data Model Addition (small, additive change to your existing schema), 7. Handling Images (Payment Slips) and Voice Notes — Both Native to Telegram (+5 more)

### Community 114 - "escalation_reasons.py"
Cohesion: 0.15
Nodes (10): CRM business logic — called by MCP server only (Week 13 pattern)., _count_rows(), dashboard_overview(), Any, DashboardTenant, get, Dashboard overview stats for staff home screen., Aggregate counts for dashboard landing page. (+2 more)

### Community 115 - "Langfuse Runtime 6"
Cohesion: 0.21
Nodes (6): parse_field_definitions(), Tenant onboarding field definitions — custom slots beyond core name/class/consen, Turn DB/CRM rows into field defs, skipping reserved core keys., TenantFieldDef, OnboardingSlots, test_required_custom_field_blocks_completion()

### Community 116 - "Dashboard Module 7"
Cohesion: 0.21
Nodes (13): consume_staff_link_code(), normalize_link_code(), _parse_channel(), _parse_dt(), Any, ChatChannel, datetime, Resolve staff from a channel address (e.g. Telegram chat_id) and consume link co (+5 more)

### Community 117 - "Dashboard Module 8"
Cohesion: 0.16
Nodes (11): _get_twilio_auth(), _is_audio_url(), _mask_phone(), _measure_audio_duration(), Speech-to-text service — download voice notes and transcribe via Gemini.  Featur, Mask phone number: +9477****567. Returns 'unknown' if None., Check if a URL points to a voice note file (.ogg/.opus) based on extension., Return (account_sid, auth_token) if configured, else None. (+3 more)

### Community 118 - "Student Chat Deps 6"
Cohesion: 0.34
Nodes (13): get_bot_token_for_tenant(), Return the Telegram bot token for ``tenant_id``.      Tokens are stored on ``ten, asyncio, Per-tenant Telegram bot token lookup tests., _tenant_client(), test_get_bot_token_for_tenant_returns_token(), test_get_bot_token_for_tenant_uses_cache(), test_get_bot_token_inactive_tenant_raises() (+5 more)

### Community 119 - "Demo Chat Lifecycle 3"
Cohesion: 0.27
Nodes (13): decide(), parametrize, Regression tests for sticky flow-state (category B in the QA log).  The reported, A typed slot value shares vocabulary with real intents; shape decides., test_b1_b3_new_requests_interrupt_a_pending_payment(), test_b5_shared_link_interrupts_every_flow(), test_conversational_replies_continue_the_flow(), test_enrollment_talk_continues_onboarding_but_interrupts_payment() (+5 more)

### Community 120 - "Chat Message Pipeline 6"
Cohesion: 0.15
Nodes (8): db_conn(), _db_url(), fixture, Validate v2 ER schema tables exist in Supabase when DATABASE_URL is configured., school and district stay real columns; extra_fields is additive only., Demo tenants keep today's school/district extras; core fields stay out., test_every_tenant_has_school_and_district_field_definitions(), test_students_keep_school_and_district_columns()

### Community 121 - "MCP Integration 5"
Cohesion: 0.42
Nodes (13): _async_client(), _json_response(), asyncio, Telegram Bot API client tests — tenant token isolation., test_download_telegram_file_uses_matching_token(), test_get_telegram_file_path(), test_send_contact_request_includes_keyboard(), test_send_telegram_chat_action_does_not_raise() (+5 more)

### Community 122 - "verify phase0 py"
Cohesion: 0.15
Nodes (12): AXIOM AI — Telegram Integration: Implementation Plan for Cursor, Explicit Non-Goals for This Task (tell Cursor not to touch these), Pre-requisites (do these manually before starting, not part of the coding task), Suggested Build Order (for a single session with Cursor), TASK 1 — Database: Add Telegram Channel Support, TASK 2 — Config: Per-Tenant Bot Token Storage & Lookup, TASK 3 — Telegram Client: Send Messages, Fetch Files, TASK 4 — Webhook Endpoint: Receive & Route Telegram Updates (+4 more)

### Community 123 - "Resource Agent 3"
Cohesion: 0.15
Nodes (13): `audit_logs` (AUDIT_LOG), `bank_slip_uploads` (BANK_SLIP_UPLOAD), `enrollments` (ENROLLMENT), `escalations` (ESCALATION), `invoices` (INVOICE), `message_logs` (MESSAGE_LOG), `parent_guardians` (PARENT_GUARDIAN), `staff_users` (STAFF_USER) (+5 more)

### Community 124 - "Dashboard Frontend Deps 2"
Cohesion: 0.15
Nodes (7): Open (or return existing) escalation for dashboard inbox., Legacy alias — creates payment_receipt escalation without bank_slip storage., Reason-aware resolve: payment → activate enrollment; tutor → close only., Staff approves payment — activates pending enrollment., Staff rejects payment — closes escalation without activating enrollment., Backward-compatible alias for payment resolve., is_payment_reason()

### Community 125 - "Dashboard Module 9"
Cohesion: 0.21
Nodes (12): analyze_tenant_faqs(), Any, DashboardTenant, Cluster recent student questions for one class into recurring FAQ themes., analyze_faqs(), _clean_message(), FAQCluster, FAQClusterOutput (+4 more)

### Community 126 - "Dashboard Module 10"
Cohesion: 0.22
Nodes (12): admissions_route_decision(), apply_onboarding_patch_overrides(), is_onboarding_active(), onboarding_router_context_hint(), Route-lock helpers — keep mid-onboarding turns on the admissions agent.  The loc, True when the message is a different request, not onboarding input., True when an in-memory onboarding session is collecting details., Force proceed + admissions when mid-onboarding. Returns True if applied. (+4 more)

### Community 127 - "Dashboard Module 11"
Cohesion: 0.23
Nodes (8): extract_docx(), _heading_level(), _looks_like_heading(), _promote_bold_headings(), DOCX → markdown via mammoth (HTML) → markdownify.  mammoth keys off Word's *sema, Turn standalone whole-line bold paragraphs into markdown headings., Extract markdown from .docx bytes., TestPromoteBoldHeadings

### Community 128 - "Dashboard API Routes 4"
Cohesion: 0.26
Nodes (8): FakeDrive, Any, asyncio, Class-scoped RAG retrieval tests., test_kb_search_forwards_class_ids_to_rag_service(), test_resource_agent_blocks_enrolled_without_class_ids(), test_resource_agent_passes_enrolled_class_ids_to_rag(), TrackingRag

### Community 129 - "Student Chat Deps 7"
Cohesion: 0.31
Nodes (12): get_onboarding_fields(), get_tenant_profile(), list_tenants(), _normalize_slug(), get, put, Session, replace_onboarding_fields() (+4 more)

### Community 130 - "Decision Graph 4"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, moduleResolution, noEmit, skipLibCheck, strict, target (+3 more)

### Community 131 - "Supabase DB Client 6"
Cohesion: 0.17
Nodes (12): Acceptance criteria mapping, Agent ownership, Core decision: escalation-only HITL, Dashboard API (implemented), Decisions explicitly skipped, Flow 1 — Payment receipt, Flow 2 — Talk to tutor, Phase 5 — Design Decisions (As Implemented) (+4 more)

### Community 132 - "P0 — Must finalize (MVP gate)"
Cohesion: 0.17
Nodes (12): 10. Phased Implementation Plan, Acceptance Criteria, Acceptance Criteria, Features, Features, Files / Modules, Objective, Objective (+4 more)

### Community 133 - "preload agent runtime"
Cohesion: 0.17
Nodes (12): 16.10 V2 Architecture Upgrades (Reference Patterns), 16.11 V2 Acceptance Themes, 16.1 Messaging & Infrastructure, 16.2 AI Agents & Orchestration, 16.3 Memory, Caching & RAG Enhancements, 16.4 Payments & Finance Automation, 16.5 Integrations & Tooling, 16.6 CRM, Dashboard & Backend APIs (Extended) (+4 more)

### Community 134 - "build_cors_origins"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 135 - "test_run_resource_agent_requires_mcp_clients_when_fallback_disabled"
Cohesion: 0.18
Nodes (9): ExtractedDoc, ExtractionError, ValueError, Shared types for document extraction.  Every extractor converts source bytes int, Raised when a document cannot be turned into usable markdown.      Subclasses Va, Normalized extraction result handed to the ingest pipeline., extract_markdown(), Markdown / plain-text passthrough. (+1 more)

### Community 136 - "Dashboard Frontend Deps 3"
Cohesion: 0.32
Nodes (11): _chain_mock(), patch, Dashboard API HTTP tests (mocked Supabase + CRM)., test_dashboard_chat_conversations(), test_dashboard_chat_logs_alias(), test_dashboard_chat_thread(), test_dashboard_overview(), test_dashboard_staff_send_returns_502_when_delivery_fails() (+3 more)

### Community 137 - "deps.py"
Cohesion: 0.27
Nodes (11): _fake_ingest_result(), _minimal_docx(), patch, Ingest pipeline unit tests., The old name is kept for one release; callers should move to run_upload_ingest., test_fixed_chunk_produces_chunks(), test_ingest_documents_parent_child(), test_parent_child_chunk_links_parent_text() (+3 more)

### Community 138 - "Dashboard Frontend Deps 4"
Cohesion: 0.33
Nodes (10): ctx(), _image(), _pipeline(), asyncio, fixture, Regression tests for inbound media handling (B6).  The reported bug: a student p, test_a_real_audio_file_still_gets_the_voice_note_hint(), test_b6_payment_slip_image_reaches_the_agent() (+2 more)

### Community 255 - "delete_chunks_by_document_id"
Cohesion: 0.15
Nodes (21): _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_chat_turns(), get_conversation_thread(), get_thread_alias(), list_conversations(), get_chat_logs() (+13 more)

### Community 256 - "test_drive_mcp_server.py"
Cohesion: 0.24
Nodes (12): clear_class_folder_cache(), chemistry_drive_backend(), _clear_drive_cache(), _load_for(), _nested(), physics_drive_backend(), fixture, Drive MCP server — tool surface and tenant/class scoping. (+4 more)

### Community 257 - "classify_media"
Cohesion: 0.21
Nodes (10): classify_media(), MediaKind, Enum, str, Classify an inbound attachment so each media type gets its own handling.  The in, Formats a bank slip plausibly arrives in., Best-effort media kind from a Content-Type header or URL extension., _suffix() (+2 more)

### Community 258 - "smoke_mcp_memory.py"
Cohesion: 0.39
Nodes (7): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory(), build_agent_mcp(), MCP path — memory tools via stdio server (Week 13 pattern).

### Community 259 - "test_media_kind.py"
Cohesion: 0.33
Nodes (10): ctx(), _image(), _pipeline(), asyncio, fixture, Regression tests for inbound media handling (B6).  The reported bug: a student p, test_a_real_audio_file_still_gets_the_voice_note_hint(), test_b6_payment_slip_image_reaches_the_agent() (+2 more)

### Community 260 - "telegram_webhook"
Cohesion: 0.22
Nodes (8): Request, Telegram Bot API webhook router — one bot (token) per tenant., Receive Telegram updates for a single tenant bot.      Always acknowledges with, telegram_webhook(), ensure_tenant_bot(), is_tenant_bot_error(), BaseException, Fail fast if this webhook path does not map to a configured tenant bot.

### Community 261 - "validate_twilio_signature"
Cohesion: 0.33
Nodes (7): Twilio request signature validation., validate_twilio_signature(), Twilio signature validation tests., _sign(), test_validate_twilio_signature_accepts_valid_signature(), test_validate_twilio_signature_rejects_invalid_signature(), test_validate_twilio_signature_rejects_tampered_body()

### Community 262 - "arithmetic.py"
Cohesion: 0.39
Nodes (7): _evaluate(), evaluate_arithmetic(), _format(), looks_like_arithmetic(), Evaluate the bare arithmetic students occasionally send.  "2+2?" was answered wi, Return the formatted result, or ``None`` if this isn't plain arithmetic., AST

### Community 263 - "main"
Cohesion: 0.38
Nodes (6): _build_analytics(), extract_phone_from_message(), format_overview_fallback(), _parse_dt(), datetime, Read-only dashboard analytics for the staff Dashboard Agent.  tenant_id is bound

### Community 264 - "ClassReference"
Cohesion: 0.29
Nodes (3): ClassReference, What a student's mention of a class resolved to., The student referred to *some* class, whether or not it exists.

### Community 265 - "Per-institute onboarding"
Cohesion: 0.33
Nodes (6): Folder ID, Folder layout, Per-institute onboarding, Share with service account, Supabase tenant row, Tutor notes (RAG, separate step)

### Community 266 - "smoke_resource.py"
Cohesion: 0.70
Nodes (4): main(), smoke_drive_mock(), smoke_ingest_load(), smoke_resource_agent()

### Community 267 - "rag.py"
Cohesion: 0.40
Nodes (4): get, Debug REST — RAG tool (same surface as rag_server MCP)., search(), status()

### Community 193 - "api/__init__.py"
Cohesion: 0.33
Nodes (5): list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant.

### Community 194 - "routers/__init__.py"
Cohesion: 0.33
Nodes (5): get_default_embeddings(), Any, OpenAI embeddings for RAG ingest and retrieval., Return configured embedding model (text-embedding-3-small by default)., OpenAIEmbeddings

### Community 195 - "routers/tools/__init__.py"
Cohesion: 0.40
Nodes (5): asyncio, parametrize, Router intent classification tests., _router_with_content(), test_router_intents()

### Community 197 - "db/__init__.py"
Cohesion: 0.40
Nodes (5): 2. LLM Model Strategy, Config Files, Merge Points (Gemini), Model Assignments (Locked for MVP), Why Two Models?

### Community 198 - "mcp_servers/__init__.py"
Cohesion: 0.40
Nodes (5): 3. Status Enums & Domain Types, Enum ↔ Langfuse Tags, PostgreSQL ENUM Types (`sql/01_schema.sql`), Python Enums (`src/domain/enums.py`), Rules

### Community 199 - "memory/__init__.py"
Cohesion: 0.40
Nodes (5): 4. Langfuse Observability & Prompt Management, Environment, Phase Deliverables for Langfuse, Prompt Management — Langfuse as Source of Truth, Tracing — Per Tenant, Session, User

### Community 200 - "drive_service/__init__.py"
Cohesion: 0.40
Nodes (5): 5. System Understanding, Agent Roster (MVP — 4 specialists + router), Business Problem, MVP Solution (AI Backend), Success Metrics (from MVP Definition)

### Community 201 - "ingest_service/__init__.py"
Cohesion: 0.40
Nodes (5): _call_gemini(), _is_retryable(), Exception, Check if an exception is transient and worth retrying., Send voice note to Gemini for transcription with retry.

### Community 202 - "src/services/__init__.py"
Cohesion: 0.40
Nodes (4): _content_type_supported(), _download_with_retry(), Check if the Content-Type header indicates a voice note (OGG Opus)., Download voice note from a URL with retry and Content-Type validation.      If a

### Community 203 - "services/prompts/__init__.py"
Cohesion: 0.50
Nodes (4): get_current_staff(), HTTPAuthorizationCredentials, Session, decode_access_token()

### Community 204 - "rag_service/__init__.py"
Cohesion: 0.50
Nodes (4): 7. Multi-Tenant Data Model, Core Entities, Shared Supabase for Dashboard Team, Tenant Resolution (Inbound Twilio)

### Community 205 - "tests/__init__.py"
Cohesion: 0.50
Nodes (4): 4.1 User Role Overview, 4.2 Student Profile, 4.3 Tutor and Agency Admin Profile, 4\. Stakeholders and User Roles

### Community 206 - "deps/__init__.py"
Cohesion: 0.50
Nodes (3): Path, Measure how many real student messages still need an LLM round trip., read_cells()

### Community 207 - "Dashboard Alembic Dependency"
Cohesion: 0.83
Nodes (3): check_live(), main(), run_pytest()

### Community 208 - "CLAUDE.md"
Cohesion: 0.50
Nodes (3): _build_user_prompt(), build_guardrail_system_prompt(), GuardrailVerdict

### Community 209 - "AI_API_BASE"
Cohesion: 0.67
Nodes (3): get_stt_metrics(), Any, Return current transcription metrics. Call from a /metrics endpoint.

### Community 210 - "DASHBOARD_API_BASE"
Cohesion: 0.50
Nodes (4): clear_bot_token_cache(), Drop cached tokens — used by tests and after rotating a token., fixture, _reset_cache()

### Community 211 - "frontend/tailwind.config.js"
Cohesion: 0.50
Nodes (4): ValueError, Raised when a tenant has no usable Telegram bot token., TenantBotTokenError, test_telegram_webhook_unknown_tenant_still_acks()

### Community 214 - "RateLimitMiddleware"
Cohesion: 0.67
Nodes (3): 10.1 Agent Roster, 10.2 Conceptual Data Flow, 10\. System Architecture Overview (High Level)

### Community 215 - "tenant_scope.py"
Cohesion: 0.67
Nodes (3): 16.1 Constraints, 16.2 Assumptions, 16\. Constraints and Assumptions

### Community 216 - "PaymentStatusUpdate"
Cohesion: 0.67
Nodes (3): 2.1 Purpose, 2.2 In Scope / Out of Scope, 2\. Purpose, Scope, and Definitions

### Community 217 - "FakeCrm"
Cohesion: 0.67
Nodes (3): 3.1 Adjacent Tools and Why They Fall Short, 3.2 Tutor AI's Differentiation, 3\. Market and Competitive Context

### Community 218 - "Testing"
Cohesion: 0.67
Nodes (3): 7.1 Student and Parent Stories, 7.2 Tutor and Admin Stories (CRM Focused), 7\. User Stories

### Community 219 - "telegram_webhook"
Cohesion: 0.67
Nodes (3): Axiom AI — Multi-Agent Backend, Docs, Quick start

## Knowledge Gaps
- **714 isolated node(s):** `name`, `private`, `version`, `type`, `description` (+709 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ChatChannel` connect `Invoice DB Layer 2` to `Test Suite 3`, `page_needs_ocr`, `Escalation Routes 4`, `Dashboard Module`, `Escalation Routes 8`, `Workshop Exploration`, `Dashboard API Routes 2`, `PaymentStatusUpdate`, `Agent Orchestrator`, `Dashboard ORM Models`, `Resource Agent 3`, `Phase 5 — Escalations + staff chat`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `ScheduleService` connect `MCP Integration 2` to `Chat Message Pipeline 7`, `Dashboard API Routes`, `RAG Ingest Pipeline 3`, `Admissions Onboarding 5`, `test_identity_recall.py`, `Drive Tooling`, `API Chat Schemas`, `Escalation Routes 7`, `Resource Agent 2`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `run_chat_turn()` connect `Admissions Onboarding 9` to `Dashboard Module 4`, `Admissions Onboarding 2`, `Demo Chat Lifecycle 2`, `decision_bridge.py`, `IdentityResolver`, `Escalation Routes`, `page_needs_ocr`, `Chat Message Pipeline 3`, `Admissions Onboarding 18`, `Decision Graph 2`, `CRM MCP Server`, `_tracing_enabled`, `Langfuse Runtime 2`, `Test Suite 2`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `OnboardingFlow` (e.g. with `main()` and `AdmissionsAgent`) actually correct?**
  _`OnboardingFlow` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 71 inferred relationships involving `get_supabase_client()` (e.g. with `main()` and `step6_tenant()`) actually correct?**
  _`get_supabase_client()` has 71 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `IdentityContext` (e.g. with `main()` and `main()`) actually correct?**
  _`IdentityContext` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `AgentState` (e.g. with `AdmissionsAgent` and `AdmissionsAgentResult`) actually correct?**
  _`AgentState` has 24 INFERRED edges - model-reasoned connections that need verification._