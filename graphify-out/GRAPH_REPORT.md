# Graph Report - .  (2026-08-06)

## Corpus Check
- Large corpus: 306 files · ~673,351 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 2247 nodes · 4081 edges · 185 communities (148 shown, 37 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 759 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

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
- Supabase DB Client 4
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
- Dashboard Module 17
- Student Chat Deps 8
- Demo UI
- Langfuse Runtime 7
- LangGraph Supervisor Orchestrator
- Sri Lankan Private
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
- AI Tutor SaaS
- OpenRouter LLM Access
- axiom ai backend

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
- `Manual Payment Verification Handoff` --semantically_similar_to--> `Escalation-Only HITL`  [INFERRED] [semantically similar]
  docs/AXIOM AI - Minimum Viable Product (MVP) Definition (Revised).pdf → docs/PHASE5_DECISIONS.md
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

## Hyperedges (group relationships)
- **Python Backend Skill Stack** — _agents_skills_python_backend_skill_fastapi, _agents_skills_python_backend_skill_sqlalchemy, _agents_skills_python_backend_skill_upstash, _agents_skills_python_backend_skill_pydantic [EXTRACTED 1.00]
- **Axiom AI Backend Stack** — agents_axiom_ai_backend, _agents_skills_python_backend_skill_fastapi, agents_langchain, agents_supabase, agents_qdrant [EXTRACTED 1.00]
- **LLM Provider Model Registries** — config_models_openrouter, config_models_openai, config_models_google, config_models_groq [EXTRACTED 1.00]
- **Demo Student Chat Flow** — demo_ui_org_readme_whatsapp_student_chat, demo_ui_org_demo_script_student_chat_demo, demo_ui_org_demo_script_demo_physics_academy, demo_ui_org_readme_post_chat, agents_axiom_ai_backend [EXTRACTED 1.00]
- **Upstash FastAPI Integration Patterns** — _agents_skills_python_backend_references_upstash_patterns_redis, _agents_skills_python_backend_references_upstash_patterns_rate_limiting, _agents_skills_python_backend_references_upstash_patterns_qstash, _agents_skills_python_backend_skill_fastapi [EXTRACTED 1.00]
- **Phase 5 Unified HITL Payment and Tutor Escalation** — docs_phase5_decisions_escalation_only_hitl, docs_phase5_decisions_payment_check_agent, docs_phase5_decisions_escalation_agent, docs_api_contract_escalation_inbox, docs_database_escalations [EXTRACTED 1.00]
- **Resource Agent Drive vs RAG Content Split** — docs_drive_integration_resource_agent, docs_drive_integration_axiom_drive_mcp, docs_drive_integration_kb_search, docs_database_qdrant_external [EXTRACTED 1.00]
- **Shared ChatPipeline for Dev Chat and Twilio** — docs_dev_chat_post_chat, docs_dev_chat_twilio_webhook, docs_dev_chat_chat_pipeline, docs_dev_chat_decision_graph [EXTRACTED 1.00]
- **Problems create opportunities that lead to ideas** — docs_screen_shot_2026_07_18_at_18_59_38_pm_problems, docs_screen_shot_2026_07_18_at_18_59_38_pm_opportunities, docs_screen_shot_2026_07_18_at_18_59_38_pm_ideas [EXTRACTED 1.00]
- **Summary principles for AI-assisted problem solving** — docs_screen_shot_2026_07_18_at_18_59_38_pm_ai_as_tool, docs_screen_shot_2026_07_18_at_18_59_38_pm_baccm, docs_screen_shot_2026_07_18_at_18_59_38_pm_diverge_on_problem, docs_screen_shot_2026_07_18_at_18_59_38_pm_problem_exploration [EXTRACTED 1.00]
- **Tutor AI Memory Layer** — docs_technical_docs_tutor_ai_er_mem_procedures, docs_technical_docs_tutor_ai_er_mem_facts, docs_technical_docs_tutor_ai_er_mem_episodes, docs_technical_docs_tutor_ai_er_st_turns [EXTRACTED 1.00]
- **Student Operational Records** — docs_technical_docs_tutor_ai_er_student, docs_technical_docs_tutor_ai_er_enrollment, docs_technical_docs_tutor_ai_er_invoice, docs_technical_docs_tutor_ai_er_message_log, docs_technical_docs_tutor_ai_er_escalation [EXTRACTED 1.00]
- **Org Tenant Core** — docs_technical_docs_tutor_ai_er_org_config, docs_technical_docs_tutor_ai_er_staff_user, docs_technical_docs_tutor_ai_er_subject_class [EXTRACTED 1.00]
- **Academic RAG Pipeline** — docs_technical_docs_userflow_generate_embedding, docs_technical_docs_userflow_search_vector_db, docs_technical_docs_userflow_retrieve_top_k_chunks, docs_technical_docs_userflow_educational_llm [EXTRACTED 1.00]
- **Intent Routes Converge at Answer Synthesis** — docs_technical_docs_userflow_educational_llm, docs_technical_docs_userflow_google_drive_search, docs_technical_docs_userflow_supabase_crm, docs_technical_docs_userflow_payhere_verification, docs_technical_docs_userflow_answer_synthesis [EXTRACTED 1.00]
- **Meta API Delivery Paths** — docs_technical_docs_userflow_return_refusal, docs_technical_docs_userflow_cached_answer, docs_technical_docs_userflow_warm_semantic_cache, docs_technical_docs_userflow_send_via_meta_api [EXTRACTED 1.00]

## Communities (185 total, 37 thin omitted)

### Community 0 - "Admissions Onboarding"
Cohesion: 0.05
Nodes (31): Pattern, main(), OnboardingFlow, OnboardingSlots, OnboardingState, Any, Multi-turn admissions onboarding — slot tracking and class disambiguation., Determine onboarding progress and extract slots from user messages. (+23 more)

### Community 1 - "Admissions Onboarding 2"
Cohesion: 0.07
Nodes (47): InfoInquiryKind, AdmissionsAgent, AdmissionsAgentResult, _last_user_text(), Any, Admissions agent node — multi-turn onboarding via CRM MCP tools., run_admissions_agent(), classify_info_inquiry() (+39 more)

### Community 2 - "Demo Chat Lifecycle"
Cohesion: 0.06
Nodes (45): QUICK_ACTIONS, detectLifecycleProgress(), emptyLifecycle(), includesAny(), LIFECYCLE_STEPS, LifecycleState, LifecycleStep, LifecycleStepId (+37 more)

### Community 3 - "RAG Ingest Pipeline"
Cohesion: 0.05
Nodes (54): ChunkStrategy, Distance, Path, QdrantClient, main(), main(), smoke_drive_mock(), smoke_ingest_load() (+46 more)

### Community 4 - "Admissions Onboarding 3"
Cohesion: 0.07
Nodes (18): CrmClient, DirectCrmClient, McpCrmClient, Any, Protocol, Shared CRM client protocol for agent nodes (direct + MCP paths)., MCP CRM tools → async dispatch., In-process CRM path (dev/tests without MCP subprocesses). (+10 more)

### Community 5 - "RAG Ingest Pipeline 2"
Cohesion: 0.07
Nodes (40): BaseChatModel, ChatOpenAI, OpenAIEmbeddings, main(), build_orchestrator(), In-process MemoryTool path (dev/tests without MCP subprocesses)., get_api_key(), get_chat_model() (+32 more)

### Community 6 - "Dashboard Frontend Pages"
Cohesion: 0.08
Nodes (41): ChatsPage(), statusClass(), ClassesPage(), ClassFormState, initialForm, OverviewData, OverviewPage(), OverviewData (+33 more)

### Community 7 - "RAG Ingest Pipeline 3"
Cohesion: 0.06
Nodes (34): BaseRetriever, Document, Runnable, Any, RagTool, RAG tool — tenant-scoped tutor-note Q&A (plain RAG, no cache)., Business logic for kb_search — used by rag_server and debug REST., format_docs() (+26 more)

### Community 8 - "Student Chat Deps"
Cohesion: 0.04
Nodes (44): autoprefixer, clsx, dependencies, clsx, framer-motion, lucide-react, react, react-dom (+36 more)

### Community 9 - "RAG Ingest Pipeline 4"
Cohesion: 0.05
Nodes (43): Alembic, Dual ID Pattern, Eager Loading, Optimistic Locking, Repository Pattern, Soft Delete Pattern, Domain-Driven Project Structure, fastapi-best-practices (+35 more)

### Community 10 - "Student Chat Deps 2"
Cohesion: 0.05
Nodes (40): chart.js, dependencies, chart.js, framer-motion, lucide-react, next, react, react-chartjs-2 (+32 more)

### Community 11 - "Student Chat Deps 3"
Cohesion: 0.06
Nodes (21): NOTE: if you add a camelCased prop to this list,, NOTE: if you add a camelCased prop to this list,, NOTE: if you add a camelCased prop to this list,, TODO: When we delete legacy mode, we should make this error argument, TODO: Remove this dead flag, TODO: Remove this dead flag, TODO: Remove outdated deferRenderPhaseUpdateToNextBatch experiment. We, NOTE: This will not work correctly for non-generic events such as `change`, (+13 more)

### Community 12 - "Admissions Onboarding 4"
Cohesion: 0.13
Nodes (18): F, AgentOrchestrator, _emit_from_config(), _format_session_memory(), _invoke_llm_text(), _last_user_text(), _llm_content_to_str(), _mcp_result_to_str() (+10 more)

### Community 13 - "Design Double Diamond"
Cohesion: 0.08
Nodes (30): Addressing the Problem, Competition Analysis, Creating Prototypes, Creative Phase, Define, Defining Requirements, Deliver, Develop (+22 more)

### Community 14 - "Design Double Diamond 2"
Cohesion: 0.14
Nodes (16): main(), main(), ChatPipeline, Channel-agnostic chat pipeline — HTTP dev chat + Twilio webhook., Sync entry for scripts and tests without a running event loop., ChatTurnResult, InboundMessage, BaseModel (+8 more)

### Community 15 - "Admissions Onboarding 5"
Cohesion: 0.12
Nodes (29): commit_onboarding(), create_enrollment(), create_escalation(), get_class_details(), get_student(), get_tenant_info(), _init(), list_classes() (+21 more)

### Community 16 - "Dashboard Frontend Deps"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 17 - "Admissions Onboarding 6"
Cohesion: 0.19
Nodes (5): get_supabase_client(), Return a singleton Supabase client (requires service role key)., AdmissionsDbClient, Any, Tenant-scoped student, class, and enrollment persistence.

### Community 18 - "Drive Tooling"
Cohesion: 0.11
Nodes (18): DriveTool, _normalize_drive_folder_id(), Any, Drive tool — tenant-scoped paper/textbook/syllabus search., Strip URL query junk users paste from Drive share links (e.g. ``?usp=drive_link`, Business logic for drive_search / drive_list — used by drive_server and REST., Find subfolder ID (papers/textbooks/syllabus) under tenant root., resolve_subfolder_id() (+10 more)

### Community 19 - "API Chat Schemas"
Cohesion: 0.29
Nodes (26): MessageRole, PaymentStatus, TenantStatus, ChatConversationsResponse, ChatConversationSummary, ChatRequest, ChatResponse, ChatThreadResponse (+18 more)

### Community 20 - "Design Double Diamond 3"
Cohesion: 0.08
Nodes (26): compilerOptions, allowImportingTsExtensions, baseUrl, isolatedModules, jsx, lib, module, moduleDetection (+18 more)

### Community 21 - "Decision Graph"
Cohesion: 0.14
Nodes (22): build_decision_graph(), build_decision_input(), decide_node(), _emit_from_config(), make_guardrail_node(), make_router_node(), Any, EmitFn (+14 more)

### Community 22 - "Dashboard ORM Models"
Cohesion: 0.09
Nodes (15): AuditLog, Base, Records all staff actions performed within the system., BankSlipUpload, Base, Represents a bank slip uploaded by a student for invoice verification., Escalation, Base (+7 more)

### Community 23 - "Admissions Onboarding 7"
Cohesion: 0.10
Nodes (26): Academic Assistant Agent, Admissions Agent, Answer Synthesis, Background Worker, Cache Hit?, Cached Response, Chat Memory, System Architecture Diagram (+18 more)

### Community 24 - "Agent Orchestrator"
Cohesion: 0.17
Nodes (15): DirectDriveClient, DirectRagClient, DriveClient, _infer_drive_folder(), _last_user_text(), _mcp_text(), Any, Protocol (+7 more)

### Community 25 - "Admissions Onboarding 8"
Cohesion: 0.10
Nodes (25): Academic Question, Admission, Answer Synthesis, Cache Hit?, Cached Answer, Educational LLM, Finance, Generate Embedding (+17 more)

### Community 26 - "Drive Tooling 2"
Cohesion: 0.14
Nodes (22): _list_children(), main(), _mask_path(), _print_summary(), TEMP DEBUG — full Google Drive MCP integration protocol (Steps 1–12).  Does not, step10b_mcp(), step12_network(), step1_environment() (+14 more)

### Community 27 - "Supabase DB Client"
Cohesion: 0.16
Nodes (16): ChatChannel, EnrollmentStatus, EscalationStatus, FeeCycle, InvoiceStatus, MessageRole, PaymentStatus, Enum (+8 more)

### Community 28 - "Agent Orchestrator 2"
Cohesion: 0.15
Nodes (13): main(), Same business logic memory_server exposes — valid when Python < 3.10., _run_mcp_adapter_path(), _run_memory_tool_fallback(), _seed_memory(), McpDriveClient, McpRagClient, AgentResponse (+5 more)

### Community 29 - "Drive Tooling 3"
Cohesion: 0.13
Nodes (16): build_drive_backend(), DriveBackend, GoogleDriveBackend, MockDriveBackend, _prefer_ipv4_for_urllib3(), Any, Protocol, Google Drive client — service account, tenant-scoped folder search. (+8 more)

### Community 30 - "Identity Context"
Cohesion: 0.15
Nodes (12): IdentityContext, Resolved tenant + student scope for one WhatsApp conversation., Resolved tenant scope; student_id is set only when a DB record exists., Stable recall key — student id when enrolled, otherwise phone., Past papers and RAG require pending or active enrollment., MessagePersistence, ChatChannel, MessageRole (+4 more)

### Community 31 - "Admissions Onboarding 9"
Cohesion: 0.16
Nodes (19): GuardrailVerdict, _build_user_prompt(), build_direct_system_prompt(), build_escalation_ack_reply(), build_guardrail_system_prompt(), build_merge_system_prompt(), build_payment_ack_reply(), build_payment_missing_media_reply() (+11 more)

### Community 32 - "Admissions Onboarding 10"
Cohesion: 0.15
Nodes (18): ChatResult, _noop_emit(), Any, EmitFn, Single async entry for one chat turn: decision graph → orchestrator (or OOS shor, _routes_from_patch(), run_chat_turn(), Agent framework — decision graph + orchestrator (Phase 2). (+10 more)

### Community 33 - "Resource Agent"
Cohesion: 0.15
Nodes (16): build_recall_context(), format_student_profile(), Build recall context (student profile + ST turns) before the decision graph., Structured student block for router and agent prompts., Return (full_router_context, student_profile_context) for one chat turn., FakeDrive, FakeMemoryTool, FakeRag (+8 more)

### Community 34 - "Chat Message Pipeline"
Cohesion: 0.14
Nodes (17): BackgroundTasks, _parse_form_params(), post, Request, Response, Twilio WhatsApp webhook router., Twilio WhatsApp sandbox webhook.      Returns 200 immediately and processes the, _should_validate_signature() (+9 more)

### Community 35 - "Invoice DB Layer"
Cohesion: 0.13
Nodes (15): get_db(), Invoice, Base, Represents a student's invoice for a specific billing period., create_invoice(), get_invoices(), get, post (+7 more)

### Community 36 - "Design Double Diamond 4"
Cohesion: 0.12
Nodes (20): AI Assisted Problem Exploration > Solution, AI Launchpad, Ascentic, Ballarat City Council Community Perceptions Theme, Benchmark Against Competitor Solutions, ChatGPT, Conduct Market Research, Customer Journey Map (+12 more)

### Community 37 - "RAG Ingest Pipeline 5"
Cohesion: 0.18
Nodes (16): main(), _mock_drive_backend(), Velocity query against real Qdrant (requires ingest + OPENAI_API_KEY)., Paper query → Drive link (mock backend; no Google credentials)., Velocity query → cited RAG answer (mocked RAG service)., smoke_drive_paper_link(), smoke_rag_velocity_live(), smoke_rag_velocity_mock() (+8 more)

### Community 38 - "Escalation Routes"
Cohesion: 0.18
Nodes (16): assign_escalation(), create_new_escalation(), get_escalations(), get_open_escalations(), get, post, put, Session (+8 more)

### Community 39 - "Chat Message Pipeline 2"
Cohesion: 0.20
Nodes (16): main(), scenario_out_of_scope(), configure_agent_runtime(), get_decision_graph(), get_orchestrator(), Lazy-init agent stack (decision graph + orchestrator) for ChatPipeline., Close MCP subprocess client on app shutdown (Week 13 / BookMe pattern)., reset_agent_runtime() (+8 more)

### Community 40 - "Invoice DB Layer 2"
Cohesion: 0.40
Nodes (17): ChatChannel, EscalationStatus, ClassBase, ClassCreate, ClassResponse, Config, EscalationCreate, EscalationResponse (+9 more)

### Community 41 - "Chat Message Pipeline 3"
Cohesion: 0.16
Nodes (15): main(), main(), _one_turn(), main(), get_chat_turns(), ChatTurnsResponse, get, Fetch recent conversation turns for a student session. (+7 more)

### Community 42 - "Dashboard ORM Models 2"
Cohesion: 0.18
Nodes (12): Enrollment, Base, Represents a student's enrollment in a subject class., EnrollmentStatus, FeeCycle, InvoiceStatus, Enum, str (+4 more)

### Community 43 - "Decision Graph 2"
Cohesion: 0.25
Nodes (5): _fallback_multi(), MultiRouteDecision, Any, QueryRouter, test_router_parses_json_routes()

### Community 44 - "Escalation Routes 2"
Cohesion: 0.21
Nodes (16): _fetch_open_escalations_by_student(), _fetch_open_escalations_for_student(), _fetch_students_by_ids(), get_chat_turns(), get_conversation_thread(), get_thread_alias(), list_conversations(), Any (+8 more)

### Community 45 - "Dashboard Module"
Cohesion: 0.16
Nodes (13): MessageLog, Base, Stores metadata about conversations between students and the AI assistant., create_message_log(), get_message_logs(), get, post, Session (+5 more)

### Community 46 - "Invoice DB Layer 3"
Cohesion: 0.28
Nodes (16): AUDIT_LOG, BANK_SLIP_UPLOAD, ENROLLMENT, ESCALATION, INVOICE, mem_episodes, mem_facts, mem_procedures (+8 more)

### Community 47 - "CRM MCP Server"
Cohesion: 0.19
Nodes (10): CrmTool, mock_db(), fixture, CRM tool and tenant isolation tests., test_create_enrollment_rejects_cross_tenant_class(), test_create_enrollment_requires_consent(), test_get_tenant_info_returns_profile(), test_list_classes_scoped_to_tenant() (+2 more)

### Community 48 - "Escalation Routes 3"
Cohesion: 0.23
Nodes (15): _enrich_escalations(), EscalationActionResponse, list_escalations(), notify_student(), Any, BaseModel, DashboardTenant, get (+7 more)

### Community 49 - "Langfuse Runtime"
Cohesion: 0.20
Nodes (14): _disable_langfuse(), get_current_trace_id(), langfuse_turn_attributes(), Any, Langfuse observability — tracing per tenant/session/user and prompt hooks.  Prom, Validate API keys once at startup; avoids repeated 401 noise from prompt fetch., OpenTelemetry / Langfuse trace id for the active context, if any., Propagate user/session/tags to nested spans for one chat turn. (+6 more)

### Community 50 - "Langfuse Runtime 2"
Cohesion: 0.20
Nodes (8): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Support Langfuse `{{var}}` and local `{var}` placeholders., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 51 - "Test Suite"
Cohesion: 0.18
Nodes (12): Depends, Resolve tenant from query param or X-Tenant-ID header.      Dashboard frontend s, Ensure the tenant exists and is active before any dashboard handler runs., require_active_tenant(), resolve_tenant_id(), patch, Tenant scope validation for dashboard endpoints., test_require_active_tenant_not_found() (+4 more)

### Community 52 - "Agent Orchestrator 3"
Cohesion: 0.19
Nodes (9): EscalationAgent, EscalationAgentResult, _last_user_text(), Escalation agent — talk-to-tutor requests → dashboard inbox., run_escalation_agent(), FakeCrm, asyncio, Escalation agent tests. (+1 more)

### Community 53 - "Admissions Onboarding 11"
Cohesion: 0.18
Nodes (9): MemEpisode, MemFact, MemProcedure, Base, Conversation summaries (episodic memory).      Each episode represents one summa, Short-term conversational memory.      Stores every conversation turn as a ring, Institution-level procedural memory.      Stores onboarding workflows, payment p, Long-term semantic memory for a specific student.      Stores distilled facts ex (+1 more)

### Community 54 - "Workshop Exploration"
Cohesion: 0.19
Nodes (14): AI Accuracy, AI as a Tool, AI Launch Pad, Ascentic, BACCM, Converge on a Problem, Diverge on a Problem, Ideas (+6 more)

### Community 55 - "Admissions Onboarding 12"
Cohesion: 0.20
Nodes (12): get_query_router(), heuristic_route(), _last_user_text(), _normalize_action(), _pattern_score(), Query Router — LLM intent classification for tuition agents.  Ported from BookMe, Deterministic routing for unambiguous tuition intents (before LLM)., router_node() (+4 more)

### Community 56 - "Supabase DB Client 2"
Cohesion: 0.19
Nodes (6): Memory business logic — called by MCP server only (Week 13 pattern)., ProceduralMemoryStore, Procedural memory store — tenant-scoped ``mem_procedures`` lookup.  Adapted from, Procedure, Memory schemas — ported from Week 13 ``memory/schemas.py`` (MVP subset)., Short-term memory store — Supabase ``st_turns`` ring buffer.  Adapted from Week

### Community 57 - "Langfuse Runtime 3"
Cohesion: 0.20
Nodes (11): Propagate tenant/session/user identifiers to all nested Langfuse observations., Langfuse trace scope for a WhatsApp conversation turn., Test helper — clear cached Langfuse client state., reset_langfuse_state(), trace_context(), TraceContext, Observability helper tests., setup_function() (+3 more)

### Community 58 - "Decision Graph 3"
Cohesion: 0.22
Nodes (10): _mock_oos_graph(), _mock_proceed_graph(), Any, asyncio, Fast E2E wiring tests (mocked LLM — BookMe / Week 13 decision_graph test pattern, Minimal stand-in — records whether orchestrator path runs (BookMe AI pattern)., _RecordingOrchestrator, test_in_scope_invokes_orchestrator() (+2 more)

### Community 59 - "Test Suite 2"
Cohesion: 0.21
Nodes (10): AnyMessage, main(), _primary_route(), RoutingCase, _run(), map_decision_to_agent_state(), Bridge decision subgraph output → orchestrator AgentState.  Ported from BookMe A, DecisionState (+2 more)

### Community 60 - "Student Chat Deps 4"
Cohesion: 0.18
Nodes (7): DashboardLayoutProps, HeaderProps, NavItem, navItems, Sidebar(), SidebarProps, cn()

### Community 61 - "Workshop Exploration 2"
Cohesion: 0.36
Nodes (13): ascentic, Business Analysis Core Competency Model (BACCM), Blue Triangle (Changes–Contexts–Stakeholders), Changes, Contexts, Dimensions of Idea Exploration, Hexagonal Star Layout, IIBA (+5 more)

### Community 62 - "RAG Tooling"
Cohesion: 0.18
Nodes (11): get_drive_tool(), get_rag_tool(), get_request_id(), Request, FastAPI dependency injection helpers., _require_startup(), get, post (+3 more)

### Community 63 - "CRM MCP Server 2"
Cohesion: 0.23
Nodes (9): Base, Represents a student registered under a tenant., Student, create_student(), get_student_by_phone(), get_students(), get, post (+1 more)

### Community 64 - "Student Chat Deps 5"
Cohesion: 0.17
Nodes (11): compilerOptions, lib, module, moduleResolution, noEmit, skipLibCheck, strict, target (+3 more)

### Community 65 - "Test Suite 3"
Cohesion: 0.23
Nodes (11): post, Staff reply to a student via WhatsApp.      Persists the message as role=system, send_staff_message(), assert_body_tenant(), assert_session_for_tenant(), Tenant scope validation for staff / dashboard endpoints., Resolved, active tenant — all dashboard queries must use this scope., Reject POST bodies whose tenant_id does not match the resolved scope. (+3 more)

### Community 66 - "IdentityResolver"
Cohesion: 0.35
Nodes (4): IdentityResolver, Any, Lookup tenant by sandbox number and student by sender phone., Resolve identity for HTTP dev chat when tenant_id is known.

### Community 67 - "Chat Message Pipeline 4"
Cohesion: 0.18
Nodes (7): parse_twilio_form(), Parse Twilio application/x-www-form-urlencoded webhook bodies., client(), identity_ctx(), fixture, Twilio webhook endpoint tests., test_parse_twilio_form_extracts_media()

### Community 68 - "Chat Turn Runner"
Cohesion: 0.18
Nodes (7): chat_result(), client(), asyncio, fixture, HTTP dev chat endpoint tests., Regression: /chat must not call asyncio.run() inside FastAPI's event loop., test_chat_pipeline_runs_agent_inside_event_loop()

### Community 69 - "Langfuse Runtime 4"
Cohesion: 0.25
Nodes (11): BaseException, get_langfuse_client(), _is_langfuse_auth_error(), is_langfuse_enabled(), langfuse_disabled_reason(), prefetch_prompts(), Return Langfuse client or None when disabled / unconfigured., Warm Langfuse prompt cache at startup. (+3 more)

### Community 70 - "MCP Integration"
Cohesion: 0.18
Nodes (8): BaseHTTPMiddleware, get, FastAPI application — Phase 6 integration (MCP warmup + dashboard APIs)., root(), Request, Response, Request ID and latency headers., RequestContextMiddleware

### Community 71 - "Dashboard API Routes"
Cohesion: 0.22
Nodes (8): Base, Represents a tuition class offered by a tenant., SubjectClass, create_class(), get_classes(), get, post, Session

### Community 72 - "Escalation Routes 4"
Cohesion: 0.22
Nodes (11): Dashboard API Contract (Phase 5), Tenant Scope Validation, Manual Payment Verification Handoff, Axiom AI MVP Definition (Revised), Staff Console Pane, Dev Chat WhatsApp Simulator, Escalation-Only HITL, No human_mode / Bot Mute (Skipped) (+3 more)

### Community 73 - "Memory MCP Path"
Cohesion: 0.25
Nodes (4): ConversationTurn, Return up to k (user, assistant) pairs — BookMe SessionStore interface., Recent conversation turns per tenant/session., ShortTermMemoryStore

### Community 74 - "Supabase DB Client 3"
Cohesion: 0.35
Nodes (10): _chain_mock(), patch, Dashboard API HTTP tests (mocked Supabase + CRM)., test_dashboard_chat_conversations(), test_dashboard_chat_logs_alias(), test_dashboard_chat_thread(), test_dashboard_overview(), test_dashboard_staff_send_returns_turn() (+2 more)

### Community 75 - "Dashboard Module 2"
Cohesion: 0.31
Nodes (9): ChatTurnRecord, Sender, build_conversation_summary(), phone_from_session_id(), Any, MessageRole, Shared helpers for dashboard chat endpoints., role_to_sender() (+1 more)

### Community 76 - "Admissions Onboarding 13"
Cohesion: 0.31
Nodes (9): add_turn(), get_procedural(), _init(), tool, Memory MCP Server — exposes ST recall / add_turn / procedural lookup.  Adapted f, Fetch recent conversation turns for a tenant session., Append a conversation turn to short-term memory., Lookup tenant onboarding / workflow procedures. (+1 more)

### Community 77 - "infrastructure config py"
Cohesion: 0.28
Nodes (9): infrastructure/config.py, LLM Roles, OpenRouter, Google Model Registry, Groq Model Registry, OpenAI Model Registry, OpenRouter Model Registry, Default Provider openai (+1 more)

### Community 78 - "Langfuse Runtime 5"
Cohesion: 0.31
Nodes (8): HealthResponse, active_config(), health(), get, Request, Health, readiness, and config endpoints., ready(), langfuse_configured()

### Community 79 - "Admissions Onboarding 14"
Cohesion: 0.53
Nodes (8): _chat(), main(), _phone(), _require_live_env(), scenario_escalation(), scenario_onboarding(), scenario_payment(), scenario_resource_rag()

### Community 80 - "Admissions Onboarding 15"
Cohesion: 0.28
Nodes (8): get_student(), Any, get, post, Student registration and lookup — dashboard + dev API., Register or update a student profile (dashboard / manual onboarding)., Fetch student profile and enrollments by phone., register_student()

### Community 81 - "Escalation Routes 5"
Cohesion: 0.22
Nodes (8): mock_db(), fixture, CRM escalation create/resolve tests for Phase 5 flows., test_create_payment_escalation(), test_create_talk_to_tutor_escalation(), test_reject_payment_escalation(), test_resolve_payment_escalation_activates_enrollment(), test_resolve_talk_to_tutor_does_not_activate_enrollment()

### Community 82 - "Escalation Routes 6"
Cohesion: 0.32
Nodes (8): A/L Physics Fee, Amount LKR 5,000.00, Bank Transfer Slip (Demo), Date 05 Aug 2026, Demo Physics Academy, PAID Status, payment_receipt Escalation Sample, Ref DPA-DEMO-2026

### Community 83 - "Escalation Routes 7"
Cohesion: 0.32
Nodes (8): create_escalation MCP Tool, Escalation Inbox (Unified HITL Queue), payment_receipt Reason Code, Staff Chat Interface, talk_to_tutor Reason Code, Escalation Agent, Payment Check Agent, Escalation Inbox CRM Requirement

### Community 84 - "Drive Tooling 4"
Cohesion: 0.25
Nodes (8): axiom-drive MCP Server, tenants.drive_folder_id, DriveTool, kb_search RAG Tool, Resource Agent Drive vs RAG Split, Google Drive MCP Live Integration (P2), MCP_INCLUDE_DRIVE=false Default, Resource Split: Google Drive vs RAG

### Community 85 - "Resource Agent 2"
Cohesion: 0.25
Nodes (7): ResourceSubPath, classify_resource_subpath(), Keyword sub-router: drive for file requests, rag for explanations., parametrize, Resource agent sub-router tests., test_classify_resource_subpath(), test_infer_drive_folder()

### Community 86 - "Dashboard Module 3"
Cohesion: 0.29
Nodes (7): _count_rows(), dashboard_overview(), Any, DashboardTenant, get, Dashboard overview stats for staff home screen., Aggregate counts for dashboard landing page.

### Community 87 - "Dashboard API Routes 2"
Cohesion: 0.29
Nodes (7): PaymentStatusUpdate, Example dashboard PATCH body using domain enums., parametrize, test_enum_values(), test_payment_status_update_accepts_enum(), test_payment_status_update_rejects_invalid(), test_tenant_summary_schema()

### Community 88 - "MCP Integration 2"
Cohesion: 0.36
Nodes (7): drive_list(), drive_search(), _init(), tool, Drive MCP Server — papers, textbooks, syllabus only., Search tenant Drive for papers, textbooks, or syllabus files. Returns shareable, List files in an allowed Drive subfolder (papers, textbooks, syllabus).

### Community 89 - "Test Suite 4"
Cohesion: 0.25
Nodes (3): client(), fixture, Phase 0 health endpoint tests.

### Community 90 - "Test Suite 5"
Cohesion: 0.25
Nodes (5): client(), fixture, patch, PDF ingest upload endpoint tests., test_ingest_upload_pdf()

### Community 91 - "Supabase DB Client 4"
Cohesion: 0.29
Nodes (4): db_conn(), _db_url(), fixture, Validate v2 ER schema tables exist in Supabase when DATABASE_URL is configured.

### Community 92 - "Design Double Diamond 5"
Cohesion: 0.29
Nodes (6): ChatRequest, ChatResponse, post, HTTP chat endpoints — WhatsApp-like dev interface (no Twilio required)., Send a student message and receive an AI reply.      Use this during development, send_chat_message()

### Community 93 - "Escalation Routes 8"
Cohesion: 0.29
Nodes (5): get, root(), escalation_websocket(), websocket, FastAPI

### Community 94 - "Escalation Routes 9"
Cohesion: 0.57
Nodes (6): get_dashboard_chat_logs(), get_dashboard_escalations(), get_dashboard_payments(), get_summary(), get, Session

### Community 96 - "Dashboard Module 4"
Cohesion: 0.33
Nodes (4): geistMono, geistSans, metadata, ThemeInitializer()

### Community 97 - "Escalation Routes 11"
Cohesion: 0.29
Nodes (7): ST + Procedural Memory Only (MVP), enrollments Table, escalations Table, st_turns Short-Term Memory, students Table, Logical Session Key {tenant_id}:{phone}, Four-Tier Memory System

### Community 98 - "Demo Chat Lifecycle 2"
Cohesion: 0.29
Nodes (7): tenant-demo-physics, Full Agent Lifecycle Demo Script, Student Chat Pane, POST /chat Endpoint, Finalize Checklist MVP Gate (P0), Five Phase 6 E2E Smoke Scenarios, fastapi Dependency

### Community 100 - "Escalation Routes 12"
Cohesion: 0.29
Nodes (4): Open (or return existing) escalation for dashboard inbox., Legacy alias — creates payment_receipt escalation without bank_slip storage., Staff rejects payment — closes escalation without activating enrollment., is_payment_reason()

### Community 101 - "Dashboard Module 5"
Cohesion: 0.29
Nodes (6): get_chat_logs(), ChatTurnsResponse, DashboardTenant, get, Dashboard chat history — legacy alias under /chat-logs., Legacy path for conversation history.      Prefer `GET /dashboard/chat/conversat

### Community 102 - "Test Suite 6"
Cohesion: 0.38
Nodes (6): active_tenant_scope(), client(), client_no_tenant_override(), fixture, Pytest bootstrap — load project .env before tests (matches api.main and scripts), HTTP client without tenant dependency override (for auth rejection tests).

### Community 103 - "Admissions Onboarding 17"
Cohesion: 0.33
Nodes (6): mem_procedures Procedural Memory, Multi-Tenancy Isolation, tenants Table, Admissions Agent, FR-PL-01 Multi-Tenant Data Isolation, Sri Lanka PDPA Compliance

### Community 104 - "MCP Integration 3"
Cohesion: 0.40
Nodes (4): LogRecord, _InterceptHandler, Centralised loguru setup (stderr-only for future MCP safety)., setup_logging()

### Community 105 - "Admissions Onboarding 18"
Cohesion: 0.33
Nodes (3): CRM business logic — called by MCP server only (Week 13 pattern)., Escalation reason codes for dashboard inbox filtering., Supabase access for admissions CRM operations.

### Community 106 - "Escalation Routes 13"
Cohesion: 0.33
Nodes (3): Reason-aware resolve: payment → activate enrollment; tutor → close only., Staff approves payment — activates pending enrollment., Backward-compatible alias for payment resolve.

### Community 107 - "Dashboard API Routes 3"
Cohesion: 0.33
Nodes (5): list_classes(), Any, get, Subject class listing — dashboard API., List available classes for a tenant.

### Community 108 - "MCP Integration 4"
Cohesion: 0.47
Nodes (5): list_files(), post, Debug REST — Drive tool (same surface as drive_server MCP)., search(), DriveResponse

### Community 109 - "RAG Ingest Pipeline 6"
Cohesion: 0.33
Nodes (5): post, Document ingest — PDF upload → parent-child chunk → Qdrant., Upload a tutor PDF, extract text, parent-child chunk, embed, and upsert to Qdran, upload_document(), UploadFile

### Community 110 - "Supabase DB Client 5"
Cohesion: 0.33
Nodes (5): list_tenants(), ping_supabase(), Any, Supabase REST client wrapper., Lightweight connectivity check via tenants table.

### Community 111 - "Test Suite 7"
Cohesion: 0.40
Nodes (5): asyncio, parametrize, Router intent classification tests., _router_with_content(), test_router_intents()

### Community 112 - "Dashboard Module 6"
Cohesion: 0.50
Nodes (5): Circular Clip Mask, Dashboard Public Asset, Globe Icon SVG, Latitude Longitude Grid, Wireframe Globe

### Community 113 - "RAG Ingest Pipeline 7"
Cohesion: 0.50
Nodes (5): Qdrant External Vector Search, Supabase PostgreSQL + pgvector, Week 07 Student Setup Guide, qdrant-client Dependency, supabase Client Dependency

### Community 114 - "Chat Message Pipeline 5"
Cohesion: 0.40
Nodes (5): ChatPipeline, Decision Graph (Guardrail || Router), POST /webhooks/twilio, Telegram Bot Integration (P2), Copy-from-Reference Policy (BookMe + Week 13)

### Community 115 - "Langfuse Runtime 6"
Cohesion: 0.60
Nodes (4): _langfuse_template(), main(), Convert Python .format `{var}` placeholders to Langfuse `{{var}}`., _seed_catalog()

### Community 116 - "Dashboard Module 7"
Cohesion: 0.83
Nodes (4): Document File Icon, Folded Page Corner, Generic Document Metaphor, Document Text Lines

### Community 117 - "Dashboard Module 8"
Cohesion: 0.67
Nodes (4): Application Window Frame, Content Pane, Title Bar Controls, Window Icon

### Community 118 - "Student Chat Deps 6"
Cohesion: 0.50
Nodes (3): __dirname, sharedDir, srcDir

### Community 119 - "Demo Chat Lifecycle 3"
Cohesion: 0.50
Nodes (4): MVP Deflection Rate >75%, MCP Lifecycle & /ready Health, Locked Architecture Decisions (MVP), MCP Tool Architecture (crm/drive/rag/memory)

### Community 120 - "Chat Message Pipeline 6"
Cohesion: 0.50
Nodes (4): Meta Webhook 3s Timeout Constraint, No Redis Message Queue (MVP), Twilio WhatsApp Sandbox Channel, FR-AI-01 Multi-Agent WhatsApp/Telegram Backend

### Community 121 - "MCP Integration 5"
Cohesion: 0.50
Nodes (4): AGENT_USE_MCP Runtime Flag, Python 3.11 Prerequisite, langchain-mcp-adapters (Python 3.10+), requirements-mcp Full MCP Stack

### Community 122 - "verify phase0 py"
Cohesion: 0.83
Nodes (3): check_live(), main(), run_pytest()

### Community 123 - "Resource Agent 3"
Cohesion: 0.50
Nodes (3): asyncio, Resource agent — in-process tools blocked when ALLOW_INPROCESS_TOOLS=false., test_run_resource_agent_requires_mcp_clients_when_fallback_disabled()

### Community 124 - "Dashboard Frontend Deps 2"
Cohesion: 0.67
Nodes (3): Dashboard Public Brand Asset, Next.js, Next.js Wordmark Logo

### Community 125 - "Dashboard Module 9"
Cohesion: 0.67
Nodes (3): Upward Triangle Mark, Vercel Logo, White Fill

### Community 130 - "Decision Graph 4"
Cohesion: 0.67
Nodes (3): Gemini 2.5 Flash Merge Model, GPT-4o-mini Chat/Router/Guardrail, Singlish / Sinhala-Tamil NLP

### Community 133 - "preload agent runtime"
Cohesion: 0.67
Nodes (3): preload_agent_runtime(), Any, Store warmed instances from FastAPI lifespan (BookMe AI ``main.py`` pattern).

## Ambiguous Edges - Review These
- `Axiom AI Backend` → `Dashboard Backend`  [AMBIGUOUS]
  AGENTS.md · relation: conceptually_related_to
- `OpenRouter` → `Default Provider openai`  [AMBIGUOUS]
  AGENTS.md · relation: conceptually_related_to
- `LLM Roles` → `Groq Model Registry`  [AMBIGUOUS]
  config/models.yaml · relation: conceptually_related_to
- `Axiom AI Setup Guide (Phase 6)` → `Tavily Web Search API`  [AMBIGUOUS]
  docs/Technical Docs/SetupGuide.pdf · relation: conceptually_related_to
- `Twilio WhatsApp Sandbox Channel` → `FR-AI-01 Multi-Agent WhatsApp/Telegram Backend`  [AMBIGUOUS]
  docs/Tutor_AI_SRS_v2.md · relation: conceptually_related_to

## Knowledge Gaps
- **253 isolated node(s):** `eslintConfig`, `nextConfig`, `name`, `version`, `private` (+248 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Axiom AI Backend` and `Dashboard Backend`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `OpenRouter` and `Default Provider openai`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `LLM Roles` and `Groq Model Registry`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Axiom AI Setup Guide (Phase 6)` and `Tavily Web Search API`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Twilio WhatsApp Sandbox Channel` and `FR-AI-01 Multi-Agent WhatsApp/Telegram Backend`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `CrmTool` connect `CRM MCP Server` to `Admissions Onboarding 16`, `Escalation Routes 12`, `Admissions Onboarding 3`, `Admissions Onboarding 18`, `Escalation Routes 13`, `Admissions Onboarding 5`, `Escalation Routes 3`, `Admissions Onboarding 6`, `Admissions Onboarding 15`, `Escalation Routes 5`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `AgentState` connect `Agent Orchestrator` to `Admissions Onboarding 10`, `Admissions Onboarding 2`, `Admissions Onboarding 3`, `RAG Ingest Pipeline 5`, `Decision Graph 2`, `Admissions Onboarding 4`, `Agent Orchestrator 3`, `Admissions Onboarding 12`, `Decision Graph 3`, `Test Suite 2`, `Agent Orchestrator 2`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._