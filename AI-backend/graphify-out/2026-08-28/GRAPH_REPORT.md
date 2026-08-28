# Graph Report - AI-backend  (2026-08-27)

## Corpus Check
- 266 files · ~451,905 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2765 nodes · 5209 edges · 198 communities (177 shown, 21 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 1092 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7970bff5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- OnboardingFlow
- ChatPage.tsx
- DriveTool
- _Query
- CrmTool
- config.py
- devDependencies
- parent_child_chunk
- _post
- CrmClient
- AdmissionsAgent
- qdrant_client.py
- api/schemas.py
- tenant_scope.py
- Axiom AI — Database Documentation
- Axiom AI Backend — Finalize Checklist
- AgentState
- get_supabase_client
- crm_server.py
- DrivePickStore
- debug_drive_integration.py
- resource_agent.py
- observability.py
- ingest_documents
- FastAPI Best Practices
- get_conversation_thread
- compilerOptions
- ShortTermMemoryStore
- test_telegram_webhook.py
- Upstash Patterns
- Google Drive MCP — Integration & Testing
- RagTool
- get_bot_token_for_tenant
- Database Patterns
- test_decision_graph.py
- Demo UI Plan — WhatsApp Mock + Full Agent Lifecycle
- Ingest v2 — Multi-format Document Ingestion
- orchestrator.py
- ChatPipeline
- AgentOrchestrator
- QueryRouter
- telegram_handlers.py
- ResourceAgent
- IdentityContext
- normalize_phone
- MessagePersistence
- sniff_format
- rag_service.py
- decision_graph.py
- institute_info.py
- runtime.py
- agent_prompts.py
- telegram_client.py
- Dev Chat — WhatsApp Simulator (No Twilio Required)
- FastAPI
- router.py
- main.py
- test_class_broadcast.py
- Dashboard API Contract (Phase 5)
- compute_document_id
- run_upload_ingest
- class_broadcast.py
- test_telegram_client.py
- run_chat_turn
- upload_document
- AXIOM AI — Twilio WhatsApp Integration Guide
- Phase 6 — Implementation Plan
- t
- dashboard/escalations.py
- extract_pdf
- test_language_mirror.py
- PromptService
- test_class_scoped_rag.py
- Axiom AI — Setup Guide (Phase 6)
- test_observability.py
- ExtractionError
- stt_service.py
- Quick Patterns
- AXIOM AI — Telegram Integration Guide
- detect.py
- test_e2e_smoke.py
- test_identity_recall.py
- AXIOM AI — Telegram Integration: Implementation Plan for Cursor
- enums.py
- _promote_bold_headings
- compilerOptions
- Phase 5 — Design Decisions (As Implemented)
- 16. Future Implementations (V2)
- Tutor_AI_SRS_v2.md
- IdentityResolver
- test_twilio_webhook.py
- test_chat.py
- test_dashboard_api.py
- .run
- AdmissionsAgentResult
- main
- kb_documents.py
- memory_server.py
- extract_document
- strip_markdown_markers
- AGENTS.md — Axiom AI Backend
- Axiom AI — AI Backend Roadmap
- Phase 0 — Foundation & Multi-Tenant Schema
- Phase 1 — Dev Chat + Messaging Pipeline *(Twilio deferred)*
- health.py
- smoke_drive_paper_link
- RateLimitMiddleware
- transcribe_audio
- SttCache
- Security Patterns
- Demo UI — WhatsApp Student Chat
- Staff chat interface
- 9\. Non-Functional Requirements
- InMemorySttCache
- build_direct_system_prompt
- post_class_broadcast
- dashboard_overview
- PaymentStatusUpdate
- rag_server.py
- _extract_llm_text
- test_schema.py
- 8.1 MCP Tool Architecture (MVP)
- Phase 2 — Agent Framework (Decision Graph + Chat Pipeline)
- Phase 4 — Resource Agent (Drive + RAG)
- get_chat_logs
- FakeCrm
- Demo script — Student chat only (~5 min)
- 10. Phased Implementation Plan
- Phase 3 — Admissions Agent
- Phase 5 — Payment Check, Escalation & Dashboard APIs
- 6\. User Journeys
- 8\. Functional Requirements
- log.py
- smoke_mcp_memory.py
- TwilioMessagingClient
- list_classes
- supabase_client.py
- test_router_intents.py
- 2. LLM Model Strategy
- 3. Status Enums & Domain Types
- 4. Langfuse Observability & Prompt Management
- 5. System Understanding
- seed_langfuse_prompts.py
- _call_gemini
- _download_with_retry
- FakeDrive
- send_chat_message
- 7. Multi-Tenant Data Model
- 4\. Stakeholders and User Roles
- verify_phase0.py
- get_stt_metrics
- vite-env.d.ts
- vite.config.ts
- 6. Resource Split: Google Drive vs RAG
- 9. High-Level Architecture
- 10\. System Architecture Overview (High Level)
- 16\. Constraints and Assumptions
- 2\. Purpose, Scope, and Definitions
- 3\. Market and Competitive Context
- 7\. User Stories
- Axiom AI — Multi-Agent Backend
- init_supabase.py
- register_telegram_webhook.py
- nodes/__init__.py
- agents/prompts/__init__.py
- tutoring_prompts.py
- dashboard/__init__.py
- routers/escalations.py
- run.py
- llm/__init__.py
- src/__init__.py
- admissions/__init__.py
- identity/__init__.py
- language/__init__.py
- media/__init__.py
- messaging/__init__.py
- rag_templates.py
- axiom-ai-backend
- crm_tool.py

## God Nodes (most connected - your core abstractions)
1. `get_supabase_client()` - 65 edges
2. `OnboardingFlow` - 57 edges
3. `AgentState` - 53 edges
4. `IdentityContext` - 52 edges
5. `CrmTool` - 41 edges
6. `MessageRole` - 38 edges
7. `ResourceAgent` - 37 edges
8. `RagTool` - 36 edges
9. `AdmissionsDbClient` - 36 edges
10. `CrmClient` - 35 edges

## Surprising Connections (you probably didn't know these)
- `test_build_resource_rag_reply_hides_internal_error()` --calls--> `build_resource_rag_reply()`  [INFERRED]
  tests/test_resource_reply_errors.py → src/agents/prompts/agent_prompts.py
- `test_build_resource_drive_list_reply_omits_links()` --calls--> `build_resource_drive_list_reply()`  [INFERRED]
  tests/test_resource_reply_errors.py → src/agents/prompts/agent_prompts.py
- `test_router_parses_json_routes()` --calls--> `QueryRouter`  [INFERRED]
  tests/test_decision_graph.py → src/agents/router.py
- `test_create_payment_escalation()` --calls--> `CrmTool`  [INFERRED]
  tests/test_payment_escalation.py → src/agents/tools/crm_tool.py
- `test_create_payment_escalation_blocked_when_payments_disabled()` --calls--> `CrmTool`  [INFERRED]
  tests/test_payment_escalation.py → src/agents/tools/crm_tool.py

## Import Cycles
- None detected.

## Communities (198 total, 21 thin omitted)

### Community 0 - "OnboardingFlow"
Cohesion: 0.06
Nodes (32): Pattern, _format_lkr_amount(), OnboardingFlow, OnboardingSlots, OnboardingState, Any, Multi-turn admissions onboarding — slot tracking and class disambiguation., Determine onboarding progress and extract slots from user messages. (+24 more)

### Community 1 - "ChatPage.tsx"
Cohesion: 0.06
Nodes (45): ApiError, BASE, chatApi, systemApi, App(), ChatWindow(), Props, DemoProgress() (+37 more)

### Community 2 - "DriveTool"
Cohesion: 0.11
Nodes (18): DriveTool, _normalize_drive_folder_id(), Any, Drive tool — tenant-scoped paper/textbook/syllabus search., Strip URL query junk users paste from Drive share links (e.g. ``?usp=drive_link`, Business logic for drive_search / drive_list — used by drive_server and REST., Find subfolder ID (papers/textbooks/syllabus) under tenant root., resolve_subfolder_id() (+10 more)

### Community 3 - "_Query"
Cohesion: 0.07
Nodes (41): bind_telegram_student_channel(), _delete_pending(), _has_enrollment(), link_telegram_contact(), _lookup_pending_phone(), _lookup_student_by_phone(), _parse_channel(), _pending_identity() (+33 more)

### Community 4 - "CrmTool"
Cohesion: 0.16
Nodes (12): CrmTool, mock_db(), fixture, CRM tool and tenant isolation tests., test_commit_onboarding_completes_unenrolled_profile(), test_commit_onboarding_rejects_already_enrolled(), test_create_enrollment_rejects_cross_tenant_class(), test_create_enrollment_requires_consent() (+4 more)

### Community 5 - "config.py"
Cohesion: 0.08
Nodes (39): BaseChatModel, ChatOpenAI, OpenAIEmbeddings, main(), get_api_key(), _get_bool(), get_chat_model(), get_embedding_model() (+31 more)

### Community 6 - "devDependencies"
Cohesion: 0.04
Nodes (44): autoprefixer, clsx, dependencies, clsx, framer-motion, lucide-react, react, react-dom (+36 more)

### Community 7 - "parent_child_chunk"
Cohesion: 0.09
Nodes (32): RecursiveCharacterTextSplitter, _breadcrumb(), _contextualize(), fixed_chunk(), _is_table_line(), _page_of(), parent_child_chunk(), Any (+24 more)

### Community 8 - "_post"
Cohesion: 0.06
Nodes (46): get_student(), Any, get, Student registration and lookup — dashboard + dev API., Register or update a student profile (dashboard / manual onboarding)., Fetch student profile and enrollments by phone., register_student(), _parse_form_params() (+38 more)

### Community 9 - "CrmClient"
Cohesion: 0.11
Nodes (8): CrmClient, DirectCrmClient, McpCrmClient, Any, Protocol, Shared CRM client protocol for agent nodes (direct + MCP paths)., MCP CRM tools → async dispatch., In-process CRM path (dev/tests without MCP subprocesses).

### Community 10 - "AdmissionsAgent"
Cohesion: 0.06
Nodes (49): InfoInquiryKind, main(), AdmissionsAgent, AdmissionsAgentResult, _last_user_text(), Any, Admissions agent node — multi-turn onboarding via CRM MCP tools., classify_info_inquiry() (+41 more)

### Community 11 - "qdrant_client.py"
Cohesion: 0.10
Nodes (41): Distance, Filter, QdrantClient, qdrant_collection_for_tenant(), point_id_for_parent(), Deterministic id for a parent-context point (stored once, joined on retrieval)., collection_exists(), collection_info() (+33 more)

### Community 12 - "api/schemas.py"
Cohesion: 0.22
Nodes (36): ChatConversationsResponse, ChatConversationSummary, ChatRequest, ChatResponse, ChatThreadResponse, ChatTurnRecord, ChatTurnsResponse, ClassBroadcastRecipient (+28 more)

### Community 13 - "tenant_scope.py"
Cohesion: 0.10
Nodes (24): Depends, _chain_mock(), main(), assert_body_tenant(), assert_form_tenant(), assert_session_for_tenant(), Tenant scope validation for staff / dashboard endpoints., Resolved, active tenant — all dashboard queries must use this scope. (+16 more)

### Community 14 - "Axiom AI — Database Documentation"
Cohesion: 0.11
Nodes (18): Application Access Patterns, Apply schema, Axiom AI — Database Documentation, Demo Seed Data, ENUM Types, ER Diagram, ER entity → SQL table mapping, Legacy v1 Tables (removed) (+10 more)

### Community 15 - "Axiom AI Backend — Finalize Checklist"
Cohesion: 0.06
Nodes (33): Agent pipeline, Axiom AI Backend — Finalize Checklist, Bot & environment, Core agent & routing, Dashboard handoff, Demo UI (`demo-ui-org/`), Documentation, Documentation sync (+25 more)

### Community 16 - "AgentState"
Cohesion: 0.15
Nodes (13): EscalationAgent, EscalationAgentResult, _last_user_text(), Escalation agent — talk-to-tutor requests → dashboard inbox., run_escalation_agent(), _last_user_text(), PaymentAgentResult, Payment Check agent — payment receipt → escalation inbox. (+5 more)

### Community 17 - "get_supabase_client"
Cohesion: 0.14
Nodes (10): get_supabase_client(), list_tenants(), ping_supabase(), Any, Supabase REST client wrapper., Return a singleton Supabase client (requires service role key)., Lightweight connectivity check via tenants table., AdmissionsDbClient (+2 more)

### Community 18 - "crm_server.py"
Cohesion: 0.12
Nodes (29): commit_onboarding(), create_enrollment(), create_escalation(), get_class_details(), get_student(), get_tenant_info(), _init(), list_classes() (+21 more)

### Community 19 - "DrivePickStore"
Cohesion: 0.06
Nodes (49): main(), _mock_drive_backend(), Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)., Paper query → Drive link (mock backend; no Google credentials)., Velocity query → cited RAG answer (mocked RAG service)., smoke_drive_paper_link(), smoke_rag_velocity_live(), smoke_rag_velocity_mock() (+41 more)

### Community 20 - "debug_drive_integration.py"
Cohesion: 0.13
Nodes (25): _list_children(), main(), _mask_path(), _print_summary(), TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).  Does not, step10b_mcp(), step12_network(), step1_environment() (+17 more)

### Community 21 - "resource_agent.py"
Cohesion: 0.15
Nodes (11): DirectRagClient, DriveClient, _last_user_text(), Protocol, RagClient, Resource agent node — Drive vs RAG sub-router via MCP tools., ResourceAgentResult, run_resource_agent() (+3 more)

### Community 22 - "observability.py"
Cohesion: 0.17
Nodes (17): _disable_langfuse(), flush(), get_current_trace_id(), langfuse_turn_attributes(), Any, Langfuse observability — tracing per tenant/session/user and prompt hooks.  Prom, Validate API keys once at startup; avoids repeated 401 noise from prompt fetch., Propagate tenant/session/user identifiers to all nested Langfuse observations. (+9 more)

### Community 23 - "ingest_documents"
Cohesion: 0.11
Nodes (28): ChunkStrategy, Path, main(), title_from_filename(), _attach_document_ids(), delete_document_ingest(), embed_texts(), ingest_documents() (+20 more)

### Community 24 - "FastAPI Best Practices"
Cohesion: 0.08
Nodes (25): API Design, Async Routes, Async Test Client from Day 0, Chain Dependencies, CPU Intensive Tasks, Custom Base Model, Decouple BaseSettings, Dependencies (+17 more)

### Community 25 - "get_conversation_thread"
Cohesion: 0.14
Nodes (24): ChatTurnRecord, Sender, _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_chat_turns(), get_conversation_thread(), get_thread_alias() (+16 more)

### Community 26 - "compilerOptions"
Cohesion: 0.08
Nodes (24): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+16 more)

### Community 27 - "ShortTermMemoryStore"
Cohesion: 0.11
Nodes (10): Memory business logic — called by MCP server only (Week 13 pattern)., ProceduralMemoryStore, Procedural memory store — tenant-scoped ``mem_procedures`` lookup.  Adapted from, ConversationTurn, Procedure, Memory schemas — ported from Week 13 ``memory/schemas.py`` (MVP subset)., Short-term memory store — Supabase ``st_turns`` ring buffer.  Adapted from Week, Return up to k (user, assistant) pairs — BookMe SessionStore interface. (+2 more)

### Community 28 - "test_telegram_webhook.py"
Cohesion: 0.17
Nodes (21): handle_text_message(), client(), _noop_typing(), asyncio, fixture, Telegram webhook + ChatPipeline wiring tests., skip_typing(), test_handle_contact_greets_already_enrolled_student() (+13 more)

### Community 29 - "Upstash Patterns"
Cohesion: 0.08
Nodes (23): Basic Setup, Batch Messages, Best Practices, FastAPI Caching, FastAPI Rate Limiting, FastAPI Session Management, Hash Operations, Key Expiration (TTL) (+15 more)

### Community 30 - "Google Drive MCP — Integration & Testing"
Cohesion: 0.08
Nodes (24): 1. Google Cloud, 2. Environment, Architecture, Folder ID, Folder layout, Google Drive MCP — Integration & Testing, Multi-tenant isolation, MVP vs v2 (+16 more)

### Community 31 - "RagTool"
Cohesion: 0.16
Nodes (12): RagTool, RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)., Business logic for kb_search — used by rag_server and debug REST., RAG MCP server — tool surface (same logic as axiom-rag stdio server)., test_rag_mcp_kb_ingest_status(), test_rag_mcp_kb_search_empty_collection(), test_rag_mcp_kb_search_with_citations(), test_rag_mcp_tenant_collections_differ() (+4 more)

### Community 32 - "get_bot_token_for_tenant"
Cohesion: 0.16
Nodes (22): clear_bot_token_cache(), _fetch_tenant_bot_row(), get_bot_token_for_tenant(), Any, ValueError, Per-tenant Telegram bot token lookup (SRS NFR-17 — not env vars)., Raised when a tenant has no usable Telegram bot token., Drop cached tokens — used by tests and after rotating a token. (+14 more)

### Community 33 - "Database Patterns"
Cohesion: 0.09
Nodes (22): Alembic Migration Naming, Async Engine + Session, Bulk Insert, Bulk Operations, Bulk Update, Cascade Delete, Commit/Rollback Pattern, Constraint Naming (+14 more)

### Community 34 - "test_decision_graph.py"
Cohesion: 0.22
Nodes (7): main(), _primary_route(), RoutingCase, _run(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, Decision subgraph state — separate from orchestrator AgentState.  Ported from Bo, AgentState — shared LangGraph state for the Axiom orchestrator.  Ported from Boo

### Community 35 - "Demo UI Plan — WhatsApp Mock + Full Agent Lifecycle"
Cohesion: 0.09
Nodes (22): 10. Technical decisions, 11. Risks & mitigations, 12. Acceptance criteria, 13. Future (post-hackathon), 1. Product concept, 2. Folder structure, 3. BookMe AI → Axiom file mapping, 4. API integration (student chat) (+14 more)

### Community 36 - "Ingest v2 — Multi-format Document Ingestion"
Cohesion: 0.09
Nodes (22): 10. Deferred to Phase 3+, 1. Where we are today, 2. Binding constraint: no torch in the runtime image, 3. Target architecture, 4. Chunking upgrade, 5. Phase 1 — extraction router, 6. Phase 2 — correctness and lifecycle, 7. Configuration (+14 more)

### Community 37 - "orchestrator.py"
Cohesion: 0.16
Nodes (14): F, run_admissions_agent(), _emit_from_config(), _format_session_memory(), _invoke_llm_text(), _last_user_text(), _llm_content_to_str(), _mcp_result_to_str() (+6 more)

### Community 38 - "ChatPipeline"
Cohesion: 0.09
Nodes (29): ChatRequest, ChatResponse, main(), main(), Send a student message and receive an AI reply.      Use this during development, send_chat_message(), IdentityContext, Resolved tenant + student scope for one WhatsApp conversation. (+21 more)

### Community 39 - "AgentOrchestrator"
Cohesion: 0.15
Nodes (14): DirectDriveClient, _mcp_text(), McpDriveClient, McpRagClient, Any, AgentOrchestrator, AgentResponse, build_agent_mcp() (+6 more)

### Community 40 - "QueryRouter"
Cohesion: 0.30
Nodes (4): _fallback_multi(), MultiRouteDecision, Any, QueryRouter

### Community 41 - "telegram_handlers.py"
Cohesion: 0.14
Nodes (20): _dispatch(), Any, Request, Telegram Bot API webhook router — one bot (token) per tenant., Receive Telegram updates for a single tenant bot.      Always acknowledges with, telegram_webhook(), _display_name(), _ensure_onboarding_session() (+12 more)

### Community 42 - "ResourceAgent"
Cohesion: 0.11
Nodes (20): main(), smoke_drive_mock(), smoke_ingest_load(), smoke_resource_agent(), build_drive_backend(), DriveBackend, GoogleDriveBackend, MockDriveBackend (+12 more)

### Community 43 - "IdentityContext"
Cohesion: 0.25
Nodes (8): build_recall_context(), format_student_profile(), Build recall context (student profile + ST turns) before the decision graph., Structured student block for router and agent prompts., Return (full_router_context, student_profile_context) for one chat turn., test_format_student_profile_enrolled(), test_format_student_profile_unknown_visitor(), test_format_student_profile_includes_language()

### Community 44 - "normalize_phone"
Cohesion: 0.14
Nodes (17): main(), main(), _one_turn(), main(), get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session. (+9 more)

### Community 45 - "MessagePersistence"
Cohesion: 0.26
Nodes (6): ChatChannel, BroadcastFailure, MessagePersistence, Return the latest turn per session_id, ordered by most recent activity., Write message_logs and st_turns rows for a conversation turn., Persist a staff-authored message (role=system → sender=staff in dashboard UI).

### Community 46 - "sniff_format"
Cohesion: 0.15
Nodes (11): _looks_like_text(), SourceType, Detect upload format from content, not from the filename.  Both the filename and, Heuristic: decodable as UTF-8 and free of NUL bytes., Return the source type for ``content``, or raise ExtractionError.      ``filenam, sniff_format(), _zip_format(), _ooxml() (+3 more)

### Community 47 - "rag_service.py"
Cohesion: 0.17
Nodes (12): BaseRetriever, Document, Runnable, build_rag_chain(), Config, Any, RAGService, Plain RAG service — Qdrant retrieval + Gemini synthesis (no CAG/CRAG). (+4 more)

### Community 48 - "decision_graph.py"
Cohesion: 0.11
Nodes (28): AnyMessage, GuardrailVerdict, map_decision_to_agent_state(), build_decision_graph(), build_decision_input(), decide_node(), _emit_from_config(), make_guardrail_node() (+20 more)

### Community 49 - "institute_info.py"
Cohesion: 0.15
Nodes (13): `audit_logs` (AUDIT_LOG), `bank_slip_uploads` (BANK_SLIP_UPLOAD), `enrollments` (ENROLLMENT), `escalations` (ESCALATION), `invoices` (INVOICE), `message_logs` (MESSAGE_LOG), `parent_guardians` (PARENT_GUARDIAN), `staff_users` (STAFF_USER) (+5 more)

### Community 50 - "runtime.py"
Cohesion: 0.20
Nodes (16): configure_agent_runtime(), get_decision_graph(), get_orchestrator(), preload_agent_runtime(), Any, Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., Store warmed instances from FastAPI lifespan (BookMe AI ``main.py`` pattern)., Close MCP subprocess client on app shutdown (Week 13 / BookMe pattern). (+8 more)

### Community 51 - "agent_prompts.py"
Cohesion: 0.19
Nodes (17): build_direct_system_prompt(), build_escalation_ack_reply(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply(), build_router_prompt(), get_admissions_stub_reply() (+9 more)

### Community 52 - "telegram_client.py"
Cohesion: 0.15
Nodes (22): download_telegram_file(), get_telegram_file_path(), _keep_telegram_typing(), Any, Response, _raise_telegram_error(), Thin Telegram Bot API client — one token per tenant, never a global token., Send a message with a one-time 'Share phone number' keyboard. (+14 more)

### Community 53 - "Dev Chat — WhatsApp Simulator (No Twilio Required)"
Cohesion: 0.17
Nodes (12): Architecture, Dev Chat — WhatsApp Simulator (No Twilio Required), Endpoints, Fetch conversation history, Prerequisites, Reference implementations, Related docs, Request body (+4 more)

### Community 54 - "FastAPI"
Cohesion: 0.09
Nodes (20): FastAPI, get_drive_tool(), get_rag_tool(), get_request_id(), Request, FastAPI dependency injection helpers., _require_startup(), HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required). (+12 more)

### Community 55 - "router.py"
Cohesion: 0.12
Nodes (21): get_query_router(), heuristic_route(), _last_user_text(), _normalize_action(), _pattern_score(), Query Router — LLM intent classification for tuition agents.  Ported from BookMe, Deterministic routing for unambiguous tuition intents (before LLM)., RouteDecision (+13 more)

### Community 56 - "main.py"
Cohesion: 0.11
Nodes (11): get, FastAPI application — Phase 6 integration (MCP warmup + dashboard APIs)., root(), BaseHTTPMiddleware, Request, Response, Request ID and latency headers., RequestContextMiddleware (+3 more)

### Community 57 - "test_class_broadcast.py"
Cohesion: 0.10
Nodes (34): BroadcastAudience, BroadcastRecipient, BroadcastResult, class_display_name(), ClassNotFoundError, _fetch_students(), _fetch_telegram_channels(), _first_name() (+26 more)

### Community 58 - "Dashboard API Contract (Phase 5)"
Cohesion: 0.08
Nodes (25): Dashboard API Contract (Phase 5), Document ingest (knowledge base), Endpoint map, Escalation inbox (unified HITL queue), Escalation object, Get thread (message panel), How to pass tenant, Integration flow (recommended) (+17 more)

### Community 59 - "compute_document_id"
Cohesion: 0.19
Nodes (12): compute_document_id(), point_id_for_chunk(), Stable document and point identity for idempotent Qdrant ingest., Content hash — same bytes always yield the same id within a tenant., Deterministic Qdrant point id so re-ingest replaces rather than duplicates., patch, Phase 2 ingest correctness — idempotency, dedup, document registry., test_compute_document_id_is_stable() (+4 more)

### Community 60 - "run_upload_ingest"
Cohesion: 0.22
Nodes (13): ExtractedDoc, Normalized extraction result handed to the ingest pipeline., _fake_ingest_result(), _minimal_docx(), patch, Ingest pipeline unit tests., The old name is kept for one release; callers should move to run_upload_ingest., test_fixed_chunk_produces_chunks() (+5 more)

### Community 61 - "class_broadcast.py"
Cohesion: 0.22
Nodes (12): main(), get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), prefetch_prompts(), BaseException, Return Langfuse client or None when disabled / unconfigured. (+4 more)

### Community 62 - "test_telegram_client.py"
Cohesion: 0.42
Nodes (13): _async_client(), _json_response(), asyncio, Telegram Bot API client tests — tenant token isolation., test_download_telegram_file_uses_matching_token(), test_get_telegram_file_path(), test_send_contact_request_includes_keyboard(), test_send_telegram_chat_action_does_not_raise() (+5 more)

### Community 63 - "run_chat_turn"
Cohesion: 0.14
Nodes (14): ConfirmationDecision, ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, _routes_from_patch(), run_chat_turn() (+6 more)

### Community 64 - "upload_document"
Cohesion: 0.19
Nodes (15): delete, delete_document(), get_document(), list_documents(), BackgroundTasks, DashboardTenant, get, Document ingest — PDF/DOCX/Markdown upload → parent-child chunk → Qdrant. (+7 more)

### Community 65 - "AXIOM AI — Twilio WhatsApp Integration Guide"
Cohesion: 0.12
Nodes (15): 10. Known Sandbox Limitations to Flag (be upfront about these, don't get caught off guard), 1. Account Setup (15–30 min), 2. How the Flow Maps to Your Existing Architecture, 3. Install Dependencies, 4. Build the Webhook Endpoint, 5. Critical Constraint: The 3-Second Webhook Window, 6. Exposing Your Local Backend to Twilio (for testing before deployment), 7. Handling Voice Notes (ties into your P0 voice transcription feature) (+7 more)

### Community 66 - "Phase 6 — Implementation Plan"
Cohesion: 0.12
Nodes (16): Acceptance criteria mapping, Explicitly out of scope (stay V2), Handoff checklist (dashboard team), Makefile targets (to add), Phase 6 — Implementation Plan, Risk register, Starting point (what’s already done), Suggested schedule (1 day) (+8 more)

### Community 67 - "t"
Cohesion: 0.21
Nodes (14): build_resource_drive_list_reply(), build_resource_drive_pick_reply(), build_resource_drive_reply(), build_resource_rag_reply(), _drive_folder_label(), get_resource_not_enrolled_reply(), _numbered_drive_names(), canned_language_parent() (+6 more)

### Community 68 - "dashboard/escalations.py"
Cohesion: 0.23
Nodes (15): _enrich_escalations(), EscalationActionResponse, list_escalations(), notify_student(), Any, BaseModel, DashboardTenant, get (+7 more)

### Community 69 - "extract_pdf"
Cohesion: 0.19
Nodes (11): PageText, One page of a paginated source document., _assemble(), extract_pdf(), _page_lacks_text(), _page_marker(), PDF → markdown via pymupdf4llm (text layer only — no vision OCR)., True when a page's text layer yielded too little to be real content. (+3 more)

### Community 70 - "test_language_mirror.py"
Cohesion: 0.19
Nodes (14): detect_script_language(), Return si/ta when native script is present; None for Latin-only text., Script of this message wins; otherwise stored preference; otherwise English., resolve_reply_language(), parametrize, Language detection, mirroring policy, routing, and canned-string eval., test_canned_templates_have_en_si_ta(), test_detect_script_latin_is_none() (+6 more)

### Community 71 - "PromptService"
Cohesion: 0.20
Nodes (8): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Support Langfuse `{{var}}` and local `{var}` placeholders., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 72 - "test_class_scoped_rag.py"
Cohesion: 0.20
Nodes (4): Open (or return existing) escalation for dashboard inbox., Legacy alias — creates payment_receipt escalation without bank_slip storage., Update student profile fields for onboarding., Atomic post-confirmation write: student profile + pending enrollment.

### Community 73 - "Axiom AI — Setup Guide (Phase 6)"
Cohesion: 0.13
Nodes (15): 10. Troubleshooting, 1. Prerequisites, 2. Clone and virtualenv, 3. Environment (`.env`), 4. Database, 5. Langfuse prompts, 6. RAG ingest (optional), 7. Run the API (+7 more)

### Community 74 - "test_observability.py"
Cohesion: 0.21
Nodes (10): Langfuse trace scope for a WhatsApp conversation turn., Test helper — clear cached Langfuse client state., reset_langfuse_state(), TraceContext, Observability helper tests., setup_function(), teardown_function(), test_trace_context_noop_when_langfuse_disabled() (+2 more)

### Community 75 - "ExtractionError"
Cohesion: 0.16
Nodes (10): ExtractionError, normalize_markdown(), ValueError, Shared types for document extraction.  Every extractor converts source bytes int, Clean up extractor output so headings are usable as breadcrumbs.      Layout-der, Raised when a document cannot be turned into usable markdown.      Subclasses Va, extract_markdown(), Markdown / plain-text passthrough. (+2 more)

### Community 76 - "stt_service.py"
Cohesion: 0.15
Nodes (12): _cache_key(), _get_twilio_auth(), _is_audio_url(), _mask_phone(), _measure_audio_duration(), Speech-to-text service — download voice notes and transcribe via Gemini.  Featur, Mask phone number: +9477****567. Returns 'unknown' if None., Check if a URL points to a voice note file (.ogg/.opus) based on extension. (+4 more)

### Community 77 - "Quick Patterns"
Cohesion: 0.14
Nodes (13): Async Routes, Core Principles, Dependency Injection, Project Structure, Pydantic Validation, python-backend, Quick Patterns, Rate Limiting (+5 more)

### Community 78 - "AXIOM AI — Telegram Integration Guide"
Cohesion: 0.14
Nodes (13): 10. Setup Checklist for Your Two-Tutor Pilot, 1. Why "One Bot Per Tutor/Institute" Is the Right Call, 2. Creating a Bot (per tutor/institute) — 2 Minutes Each, 3. Webhook Architecture — One Endpoint, Tenant Identified by URL Path, 4. Sending Responses Back, 5. Solving Your Core Requirement: Identifying the Student by Phone Number, 6. Data Model Addition (small, additive change to your existing schema), 7. Handling Images (Payment Slips) and Voice Notes — Both Native to Telegram (+5 more)

### Community 79 - "detect.py"
Cohesion: 0.23
Nodes (13): _latin_tokens(), looks_like_singlish(), looks_like_tanglish(), Reply-language resolution for Sinhala, Tamil, English, and code-switching.  Nati, True for romanized Sinhala mix (Singlish), not native Sinhala script., True for romanized Tamil mix (Tanglish), not native Tamil script., Locale for canned (non-LLM) strings, including latin Singlish/Tanglish., English-biased search string for tutor notes; keep the original as the LLM quest (+5 more)

### Community 80 - "test_e2e_smoke.py"
Cohesion: 0.18
Nodes (12): ctx(), _mock_oos_graph(), _mock_proceed_graph(), Any, asyncio, fixture, Fast E2E wiring tests (mocked LLM — BookMe / Week 13 decision_graph test pattern, Minimal stand-in — records whether orchestrator path runs (BookMe AI pattern). (+4 more)

### Community 81 - "test_identity_recall.py"
Cohesion: 0.13
Nodes (16): IdentityResolver, Any, Lookup tenant by sandbox number and student by sender phone., Resolve identity for HTTP dev chat when tenant_id is known., FakeDrive, FakeMemoryTool, FakeRag, asyncio (+8 more)

### Community 82 - "AXIOM AI — Telegram Integration: Implementation Plan for Cursor"
Cohesion: 0.15
Nodes (12): AXIOM AI — Telegram Integration: Implementation Plan for Cursor, Explicit Non-Goals for This Task (tell Cursor not to touch these), Pre-requisites (do these manually before starting, not part of the coding task), Suggested Build Order (for a single session with Cursor), TASK 1 — Database: Add Telegram Channel Support, TASK 2 — Config: Per-Tenant Bot Token Storage & Lookup, TASK 3 — Telegram Client: Send Messages, Fetch Files, TASK 4 — Webhook Endpoint: Receive & Route Telegram Updates (+4 more)

### Community 83 - "enums.py"
Cohesion: 0.22
Nodes (10): Enum, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, Domain status enums — mirror PostgreSQL ENUM types in sql/01_schema.sql., StaffRole, Domain types — enums and value objects. (+2 more)

### Community 84 - "_promote_bold_headings"
Cohesion: 0.23
Nodes (8): extract_docx(), _heading_level(), _looks_like_heading(), _promote_bold_headings(), DOCX → markdown via mammoth (HTML) → markdownify.  mammoth keys off Word's *sema, Turn standalone whole-line bold paragraphs into markdown headings., Extract markdown from .docx bytes., TestPromoteBoldHeadings

### Community 85 - "compilerOptions"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, moduleResolution, noEmit, skipLibCheck, strict, target (+3 more)

### Community 86 - "Phase 5 — Design Decisions (As Implemented)"
Cohesion: 0.17
Nodes (12): Acceptance criteria mapping, Agent ownership, Core decision: escalation-only HITL, Dashboard API (implemented), Decisions explicitly skipped, Flow 1 — Payment receipt, Flow 2 — Talk to tutor, Phase 5 — Design Decisions (As Implemented) (+4 more)

### Community 87 - "16. Future Implementations (V2)"
Cohesion: 0.17
Nodes (12): 16.10 V2 Architecture Upgrades (Reference Patterns), 16.11 V2 Acceptance Themes, 16.1 Messaging & Infrastructure, 16.2 AI Agents & Orchestration, 16.3 Memory, Caching & RAG Enhancements, 16.4 Payments & Finance Automation, 16.5 Integrations & Tooling, 16.6 CRM, Dashboard & Backend APIs (Extended) (+4 more)

### Community 88 - "Tutor_AI_SRS_v2.md"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 89 - "IdentityResolver"
Cohesion: 0.31
Nodes (6): PaymentAgent, FakeCrm, asyncio, Payment Check agent tests., test_payment_agent_creates_escalation_with_media(), test_payment_agent_requires_media()

### Community 90 - "test_twilio_webhook.py"
Cohesion: 0.20
Nodes (9): mock_db(), fixture, CRM escalation create/resolve tests for Phase 5 flows., test_create_payment_escalation(), test_create_payment_escalation_blocked_when_payments_disabled(), test_create_talk_to_tutor_escalation(), test_reject_payment_escalation(), test_resolve_payment_escalation_activates_enrollment() (+1 more)

### Community 91 - "test_chat.py"
Cohesion: 0.13
Nodes (8): BaseHTTPMiddleware, Request, Response, RateLimitMiddleware, chat_result(), client(), fixture, HTTP dev chat endpoint tests.

### Community 92 - "test_dashboard_api.py"
Cohesion: 0.32
Nodes (11): _chain_mock(), patch, Dashboard API HTTP tests (mocked Supabase + CRM)., test_dashboard_chat_conversations(), test_dashboard_chat_logs_alias(), test_dashboard_chat_thread(), test_dashboard_overview(), test_dashboard_staff_send_returns_502_when_delivery_fails() (+3 more)

### Community 93 - ".run"
Cohesion: 0.22
Nodes (8): ResourceSubPath, classify_resource_subpath(), _infer_drive_folder(), Keyword sub-router: drive for file requests, rag for explanations., parametrize, Resource agent sub-router tests., test_classify_resource_subpath(), test_infer_drive_folder()

### Community 94 - "AdmissionsAgentResult"
Cohesion: 0.22
Nodes (5): Reason-aware resolve: payment → activate enrollment; tutor → close only., Staff approves payment — activates pending enrollment., Staff rejects payment — closes escalation without activating enrollment., Backward-compatible alias for payment resolve., is_payment_reason()

### Community 96 - "main"
Cohesion: 0.47
Nodes (9): _chat(), main(), _phone(), _require_live_env(), scenario_escalation(), scenario_onboarding(), scenario_out_of_scope(), scenario_payment() (+1 more)

### Community 97 - "kb_documents.py"
Cohesion: 0.40
Nodes (9): delete_document(), get_document(), list_documents(), mark_failed(), _now_iso(), Any, Supabase registry for ingested tutor documents., registry_available() (+1 more)

### Community 98 - "memory_server.py"
Cohesion: 0.31
Nodes (9): add_turn(), get_procedural(), _init(), tool, Memory MCP Server — exposes ST recall / add_turn / procedural lookup.  Adapted f, Fetch recent conversation turns for a tenant session., Append a conversation turn to short-term memory., Lookup tenant onboarding / workflow procedures. (+1 more)

### Community 99 - "extract_document"
Cohesion: 0.27
Nodes (6): extract_document(), max_upload_bytes(), SourceType, Multi-format document extraction — PDF, DOCX and Markdown to markdown.  Every ex, Sniff the format of ``content`` and extract it to markdown.      Raises Extracti, TestExtractDocument

### Community 100 - "strip_markdown_markers"
Cohesion: 0.27
Nodes (8): Normalize student-facing chat text for WhatsApp and Telegram., Remove markdown ``**bold**`` markers so they do not show as raw asterisks., strip_markdown_markers(), Plain-text sanitizer for student-facing messages., test_empty_and_none_safe(), test_leaves_plain_text_unchanged(), test_strips_bold_markers(), test_strips_multiple_bold_spans()

### Community 101 - "AGENTS.md — Axiom AI Backend"
Cohesion: 0.22
Nodes (8): AGENTS.md — Axiom AI Backend, Environment, Gotchas, Linting, LLM Providers, Project Structure, Quick Commands, Testing

### Community 102 - "Axiom AI — AI Backend Roadmap"
Cohesion: 0.22
Nodes (9): 11. API Contract Summary (Dashboard Team), 12. Environment Variables, 13. Explicitly Out of MVP Scope, 14. Per-Phase Workflow, 15. Day-by-Day Schedule, 1. Locked Architecture Decisions, Appendix: Generic Template, Axiom AI — AI Backend Roadmap (+1 more)

### Community 103 - "Phase 0 — Foundation & Multi-Tenant Schema"
Cohesion: 0.22
Nodes (9): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 0 — Foundation & Multi-Tenant Schema, Reference Implementation (copy — do not invent) (+1 more)

### Community 104 - "Phase 1 — Dev Chat + Messaging Pipeline *(Twilio deferred)*"
Cohesion: 0.22
Nodes (9): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 1 — Dev Chat + Messaging Pipeline *(Twilio deferred)*, Reference Implementation (copy — do not invent) (+1 more)

### Community 105 - "health.py"
Cohesion: 0.31
Nodes (8): HealthResponse, active_config(), health(), get, Request, Health, readiness, and config endpoints., ready(), langfuse_configured()

### Community 106 - "smoke_drive_paper_link"
Cohesion: 0.36
Nodes (7): drive_list(), drive_search(), _init(), tool, Drive MCP Server — papers, textbooks, syllabus only., Search tenant Drive for papers, textbooks, or syllabus files. Returns shareable, List files in an allowed Drive subfolder (papers, textbooks, syllabus).

### Community 107 - "RateLimitMiddleware"
Cohesion: 0.29
Nodes (7): Dashboard overview & chat logs, Escalations (payment + talk-to-tutor), Flow 1 — Payment receipt → dashboard inbox, Flow 2 — Talk to tutor, Phase 5 — Escalations + staff chat, Staff chat (dashboard integration), Staff reply

### Community 108 - "transcribe_audio"
Cohesion: 0.31
Nodes (4): Download a voice note and transcribe via Gemini.      Args:         media_url: V, Simple counters for transcription metrics., SttMetrics, transcribe_audio()

### Community 109 - "SttCache"
Cohesion: 0.25
Nodes (5): ABC, Abstract cache for idempotency. Implement get/set/delete for Redis/DB., Return cached transcript, or None if miss/expired., Store value with TTL in seconds. value=None means 'in-progress'., SttCache

### Community 110 - "Security Patterns"
Cohesion: 0.25
Nodes (7): API Key Auth via Header, CORS Configuration, FastAPI OAuth2 Bearer Dependency, Hide OpenAPI Docs by Default, JWT Create/Verify (python-jose), Password Hashing (passlib + bcrypt), Security Patterns

### Community 111 - "Demo UI — WhatsApp Student Chat"
Cohesion: 0.25
Nodes (7): Build, Demo UI — WhatsApp Student Chat, Env (optional), Features, Prerequisites, Project layout, Quick start

### Community 112 - "Staff chat interface"
Cohesion: 0.38
Nodes (6): active_tenant_scope(), client(), client_no_tenant_override(), fixture, Shared pytest bootstrap., # IMPORTANT:

### Community 113 - "9\. Non-Functional Requirements"
Cohesion: 0.25
Nodes (8): 9.1 Usability and Accessibility, 9.2 Performance and Scalability, 9.3 Reliability and Availability, 9.4 Security, 9.5 Data Privacy and Regulatory Compliance, 9.6 Messaging and AI Cost Governance (New), 9.7 Maintainability and Observability, 9\. Non-Functional Requirements

### Community 114 - "InMemorySttCache"
Cohesion: 0.29
Nodes (4): Lock, InMemorySttCache, In-memory cache with TTL. Replace with RedisSttCache for production., Get or create a per-key lock for concurrency control.

### Community 115 - "build_direct_system_prompt"
Cohesion: 0.18
Nodes (11): get_out_of_scope_reply(), language_policy_block(), normalize_language_pref(), Human-readable hint for STT. None for English so Gemini auto-detects., Mandatory generation rule appended to LLM-facing system prompts., Map stored / incoming codes to en | si | ta. Unknown values become en., stt_language_hint(), test_language_policy_mentions_pref_and_code_switch() (+3 more)

### Community 116 - "post_class_broadcast"
Cohesion: 0.29
Nodes (7): get_broadcast_recipients(), post_class_broadcast(), DashboardTenant, get, Staff class broadcast to Telegram-linked students., Preview who would receive a Telegram class announcement., Send a class announcement to Telegram-linked enrolled students.

### Community 117 - "dashboard_overview"
Cohesion: 0.29
Nodes (7): _count_rows(), dashboard_overview(), Any, DashboardTenant, get, Dashboard overview stats for staff home screen., Aggregate counts for dashboard landing page.

### Community 118 - "PaymentStatusUpdate"
Cohesion: 0.29
Nodes (7): PaymentStatusUpdate, Example dashboard PATCH body using domain enums., parametrize, test_enum_values(), test_payment_status_update_accepts_enum(), test_payment_status_update_rejects_invalid(), test_tenant_summary_schema()

### Community 119 - "rag_server.py"
Cohesion: 0.36
Nodes (7): _init(), kb_ingest_status(), kb_search(), tool, RAG MCP Server — tenant-scoped tutor-note Q&A., Search tutor lesson notes (Qdrant) and return a grounded answer with citations., Return Qdrant ingest status for a tenant's tutor-note collection.

### Community 120 - "_extract_llm_text"
Cohesion: 0.36
Nodes (7): _extract_llm_text(), Normalize Gemini/LangChain output to a string.      Gemini 3.x returns ``AIMessa, STT Gemini response parsing tests., test_extract_llm_text_empty_blocks(), test_extract_llm_text_from_content_blocks(), test_extract_llm_text_from_string_content(), test_extract_llm_text_prefers_text_property()

### Community 121 - "test_schema.py"
Cohesion: 0.29
Nodes (4): db_conn(), _db_url(), fixture, Validate v2 ER schema tables exist in Supabase when DATABASE_URL is configured.

### Community 122 - "8.1 MCP Tool Architecture (MVP)"
Cohesion: 0.29
Nodes (7): 8.1 MCP Tool Architecture (MVP), 8. Reference Patterns to Reuse, Debug / REST parity, `mcp_config.py`, MCP servers (MVP scope), Tenant context, Wiring pattern

### Community 123 - "Phase 2 — Agent Framework (Decision Graph + Chat Pipeline)"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Dependencies, Features, Files / Modules, Objective, Phase 2 — Agent Framework (Decision Graph + Chat Pipeline), Reference Implementation (copy — do not invent)

### Community 124 - "Phase 4 — Resource Agent (Drive + RAG)"
Cohesion: 0.29
Nodes (7): Acceptance Criteria, Features, Files / Modules, Google Drive MVP Approach, Objective, Phase 4 — Resource Agent (Drive + RAG), Reference Implementation (copy — do not invent)

### Community 125 - "get_chat_logs"
Cohesion: 0.29
Nodes (6): get_chat_logs(), ChatTurnsResponse, DashboardTenant, get, Dashboard chat history — legacy alias under /chat-logs., Legacy path for conversation history.      Prefer `GET /dashboard/chat/conversat

### Community 126 - "FakeCrm"
Cohesion: 0.33
Nodes (4): FakeCrm, asyncio, Escalation agent tests., test_escalation_agent_creates_talk_to_tutor_ticket()

### Community 127 - "Demo script — Student chat only (~5 min)"
Cohesion: 0.33
Nodes (5): Demo script — Student chat only (~5 min), Narrative, Payment approval (outside this UI), Steps, Troubleshooting

### Community 128 - "10. Phased Implementation Plan"
Cohesion: 0.33
Nodes (6): 10. Phased Implementation Plan, Acceptance Criteria, Features, Objective, Phase 6 — Integration, Testing & Handoff, Reference Implementation (copy — do not invent)

### Community 129 - "Phase 3 — Admissions Agent"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features, Files / Modules, Objective, Phase 3 — Admissions Agent, Reference Implementation (copy — do not invent)

### Community 130 - "Phase 5 — Payment Check, Escalation & Dashboard APIs"
Cohesion: 0.33
Nodes (6): Acceptance Criteria, Features *(original plan — see PHASE5_DECISIONS.md for what changed)*, Files / Modules, Objective, Phase 5 — Payment Check, Escalation & Dashboard APIs, Reference Implementation (copy — do not invent)

### Community 131 - "6\. User Journeys"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 132 - "8\. Functional Requirements"
Cohesion: 0.33
Nodes (6): 8.1 Agentic Workforce and Conversational Interface, 8.2 Financial and Ticket Management, 8.3 Administrative Dashboard and Agency CRM, 8.5 Marketing and Lead Management, 8.6 Platform Administration and Multi-Tenancy (New), 8\. Functional Requirements

### Community 133 - "log.py"
Cohesion: 0.40
Nodes (4): LogRecord, _InterceptHandler, Centralised loguru setup (stderr-only for future MCP safety)., setup_logging()

### Community 134 - "smoke_mcp_memory.py"
Cohesion: 0.60
Nodes (5): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory()

### Community 135 - "TwilioMessagingClient"
Cohesion: 0.40
Nodes (5): `mem_episodes`, `mem_facts`, `mem_procedures`, Memory Tables, `st_turns`

### Community 137 - "supabase_client.py"
Cohesion: 0.50
Nodes (4): _format_citation_label(), format_docs(), RAG helper utilities., Format LangChain documents into a single context block.

### Community 138 - "test_router_intents.py"
Cohesion: 0.40
Nodes (5): asyncio, parametrize, Router intent classification tests., _router_with_content(), test_router_intents()

### Community 139 - "2. LLM Model Strategy"
Cohesion: 0.40
Nodes (5): 2. LLM Model Strategy, Config Files, Merge Points (Gemini), Model Assignments (Locked for MVP), Why Two Models?

### Community 140 - "3. Status Enums & Domain Types"
Cohesion: 0.40
Nodes (5): 3. Status Enums & Domain Types, Enum ↔ Langfuse Tags, PostgreSQL ENUM Types (`sql/01_schema.sql`), Python Enums (`src/domain/enums.py`), Rules

### Community 141 - "4. Langfuse Observability & Prompt Management"
Cohesion: 0.40
Nodes (5): 4. Langfuse Observability & Prompt Management, Environment, Phase Deliverables for Langfuse, Prompt Management — Langfuse as Source of Truth, Tracing — Per Tenant, Session, User

### Community 142 - "5. System Understanding"
Cohesion: 0.40
Nodes (5): 5. System Understanding, Agent Roster (MVP — 4 specialists + router), Business Problem, MVP Solution (AI Backend), Success Metrics (from MVP Definition)

### Community 143 - "seed_langfuse_prompts.py"
Cohesion: 0.60
Nodes (4): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog()

### Community 144 - "_call_gemini"
Cohesion: 0.40
Nodes (5): _call_gemini(), _is_retryable(), Exception, Check if an exception is transient and worth retrying., Send voice note to Gemini for transcription with retry.

### Community 145 - "_download_with_retry"
Cohesion: 0.40
Nodes (4): _content_type_supported(), _download_with_retry(), Check if the Content-Type header indicates a voice note (OGG Opus)., Download voice note from a URL with retry and Content-Type validation.      If a

### Community 146 - "FakeDrive"
Cohesion: 0.19
Nodes (9): ErrorRag, FakeDrive, asyncio, User-facing resource agent reply error sanitization., test_build_resource_drive_list_reply_omits_links(), test_build_resource_drive_reply_hides_internal_error(), test_build_resource_rag_reply_hides_internal_error(), test_kb_search_returns_generic_error_code() (+1 more)

### Community 147 - "send_chat_message"
Cohesion: 0.50
Nodes (4): asyncio, Merge response node tests., test_merge_multiple_fragments_uses_gemini(), test_merge_single_fragment_passthrough()

### Community 148 - "7. Multi-Tenant Data Model"
Cohesion: 0.50
Nodes (4): 7. Multi-Tenant Data Model, Core Entities, Shared Supabase for Dashboard Team, Tenant Resolution (Inbound Twilio)

### Community 149 - "4\. Stakeholders and User Roles"
Cohesion: 0.50
Nodes (4): 4.1 User Role Overview, 4.2 Student Profile, 4.3 Tutor and Agency Admin Profile, 4\. Stakeholders and User Roles

### Community 150 - "verify_phase0.py"
Cohesion: 0.83
Nodes (3): check_live(), main(), run_pytest()

### Community 151 - "get_stt_metrics"
Cohesion: 0.67
Nodes (3): get_stt_metrics(), Any, Return current transcription metrics. Call from a /metrics endpoint.

### Community 154 - "6. Resource Split: Google Drive vs RAG"
Cohesion: 0.67
Nodes (3): 6. Resource Split: Google Drive vs RAG, Google Drive — Tutes & Textbooks Only, RAG (Qdrant) — Tutor Notes Only

### Community 155 - "9. High-Level Architecture"
Cohesion: 0.67
Nodes (3): 9. High-Level Architecture, Decision Graph — BookMe-AI Pattern (No CAG/CRAG), Processing Model (No Redis)

### Community 156 - "10\. System Architecture Overview (High Level)"
Cohesion: 0.67
Nodes (3): 10.1 Agent Roster, 10.2 Conceptual Data Flow, 10\. System Architecture Overview (High Level)

### Community 157 - "16\. Constraints and Assumptions"
Cohesion: 0.67
Nodes (3): 16.1 Constraints, 16.2 Assumptions, 16\. Constraints and Assumptions

### Community 158 - "2\. Purpose, Scope, and Definitions"
Cohesion: 0.67
Nodes (3): 2.1 Purpose, 2.2 In Scope / Out of Scope, 2\. Purpose, Scope, and Definitions

### Community 159 - "3\. Market and Competitive Context"
Cohesion: 0.67
Nodes (3): 3.1 Adjacent Tools and Why They Fall Short, 3.2 Tutor AI's Differentiation, 3\. Market and Competitive Context

### Community 160 - "7\. User Stories"
Cohesion: 0.67
Nodes (3): 7.1 Student and Parent Stories, 7.2 Tutor and Admin Stories (CRM Focused), 7\. User Stories

### Community 161 - "Axiom AI — Multi-Agent Backend"
Cohesion: 0.67
Nodes (3): Axiom AI — Multi-Agent Backend, Docs, Quick start

## Knowledge Gaps
- **509 isolated node(s):** `name`, `private`, `version`, `type`, `description` (+504 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_supabase_client()` connect `get_supabase_client` to `get_bot_token_for_tenant`, `kb_documents.py`, `DriveTool`, `_Query`, `dashboard/escalations.py`, `normalize_phone`, `tenant_scope.py`, `MessagePersistence`, `test_identity_recall.py`, `debug_drive_integration.py`, `dashboard_overview`, `get_conversation_thread`, `ShortTermMemoryStore`, `test_class_broadcast.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `CrmTool` connect `CrmTool` to `dashboard/escalations.py`, `crm_tool.py`, `test_class_scoped_rag.py`, `CrmClient`, `_post`, `get_supabase_client`, `crm_server.py`, `test_twilio_webhook.py`, `AdmissionsAgentResult`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `IdentityContext` connect `ChatPipeline` to `main`, `_post`, `IdentityContext`, `MessagePersistence`, `test_e2e_smoke.py`, `test_identity_recall.py`, `router.py`, `test_class_broadcast.py`, `class_broadcast.py`, `run_chat_turn`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 61 inferred relationships involving `get_supabase_client()` (e.g. with `main()` and `step6_tenant()`) actually correct?**
  _`get_supabase_client()` has 61 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `OnboardingFlow` (e.g. with `main()` and `AdmissionsAgent`) actually correct?**
  _`OnboardingFlow` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `AgentState` (e.g. with `AdmissionsAgent` and `AdmissionsAgentResult`) actually correct?**
  _`AgentState` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `IdentityContext` (e.g. with `main()` and `main()`) actually correct?**
  _`IdentityContext` has 24 INFERRED edges - model-reasoned connections that need verification._