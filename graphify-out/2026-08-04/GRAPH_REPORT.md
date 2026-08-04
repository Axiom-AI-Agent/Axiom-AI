# Graph Report - Axiom-AI  (2026-08-04)

## Corpus Check
- 41 files · ~362,894 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 552 nodes · 652 edges · 69 communities (62 shown, 7 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 36 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8f1eeca1`
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

## God Nodes (most connected - your core abstractions)
1. `Week 13 Technical Documentation` - 34 edges
2. `Axiom AI — AI Backend Roadmap` - 19 edges
3. `23. Important Classes` - 18 edges
4. `3. Folder-by-Folder Explanation` - 16 edges
5. `Appendix: Complete File Inventory` - 15 edges
6. `Infrastructure Support` - 14 edges
7. `16. Future Implementations (V2)` - 12 edges
8. `_build_llm()` - 11 edges
9. `Chat Flow` - 11 edges
10. `Retrieval and Ingestion` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_validate_creates_directories()` --calls--> `validate()`  [INFERRED]
  tests/test_config.py → src/infrastructure/config.py
- `test_payment_status_update_accepts_enum()` --calls--> `PaymentStatusUpdate`  [INFERRED]
  tests/test_enums.py → src/api/schemas.py
- `test_payment_status_update_rejects_invalid()` --calls--> `PaymentStatusUpdate`  [INFERRED]
  tests/test_enums.py → src/api/schemas.py
- `test_tenant_summary_schema()` --calls--> `TenantSummary`  [INFERRED]
  tests/test_enums.py → src/api/schemas.py
- `test_trace_context_tags_and_metadata()` --calls--> `TraceContext`  [INFERRED]
  tests/test_observability.py → src/infrastructure/observability.py

## Import Cycles
- None detected.

## Communities (69 total, 7 thin omitted)

### Community 0 - "Roadmap.md"
Cohesion: 0.05
Nodes (43): 10. Phased Implementation Plan, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria (+35 more)

### Community 1 - "Infrastructure Support"
Cohesion: 0.05
Nodes (38): 4. File-by-File Explanation, Agent Core, Backend Entry and Transport, Chat Flow, MCP Servers, [src/agents/decision_graph.py](src/agents/decision_graph.py), [src/agents/guardrail.py](src/agents/guardrail.py), [src/agents/orchestrator.py](src/agents/orchestrator.py) (+30 more)

### Community 2 - "23. Important Classes"
Cohesion: 0.11
Nodes (18): 23. Important Classes, [src/agents/guardrail.py](src/agents/guardrail.py), [src/agents/orchestrator.py](src/agents/orchestrator.py), [src/agents/router.py](src/agents/router.py), [src/memory/memory_ops.py](src/memory/memory_ops.py), [src/memory/schemas.py](src/memory/schemas.py), [src/services/chat_service/cag_cache.py](src/services/chat_service/cag_cache.py), [src/services/chat_service/cag_service.py](src/services/chat_service/cag_service.py) (+10 more)

### Community 3 - "Tasks"
Cohesion: 0.18
Nodes (10): 11. API Contract Summary (Dashboard Team), 12. Environment Variables, 13. Explicitly Out of MVP Scope, 14. Per-Phase Workflow, 15. Day-by-Day Schedule, 1. Locked Architecture Decisions, 8. Reference Patterns to Reuse, Appendix: Generic Template (+2 more)

### Community 4 - "Tasks"
Cohesion: 0.14
Nodes (14): Infrastructure Support, [src/infrastructure/config.py](src/infrastructure/config.py), [src/infrastructure/db/crm_init.py](src/infrastructure/db/crm_init.py), [src/infrastructure/db/crm_models.py](src/infrastructure/db/crm_models.py), [src/infrastructure/db/qdrant_client.py](src/infrastructure/db/qdrant_client.py), [src/infrastructure/db/sql_client.py](src/infrastructure/db/sql_client.py), [src/infrastructure/db/supabase_client.py](src/infrastructure/db/supabase_client.py), [src/infrastructure/db/supabase_schema.py](src/infrastructure/db/supabase_schema.py) (+6 more)

### Community 5 - "3. Folder-by-Folder Explanation"
Cohesion: 0.12
Nodes (16): 3. Folder-by-Folder Explanation, [config](config), [docker](docker), [notebooks](notebooks), Root Files, [scripts](scripts), [sql](sql), [src/agents](src/agents) (+8 more)

### Community 6 - "Tasks"
Cohesion: 0.08
Nodes (30): F, FastAPI, LogRecord, get_request_id(), Request, FastAPI dependency injection helpers., _require_startup(), lifespan() (+22 more)

### Community 7 - "Appendix: Complete File Inventory"
Cohesion: 0.13
Nodes (15): Appendix: Complete File Inventory, config, docker, notebooks, Root, scripts, sql, src/agents (+7 more)

### Community 8 - "Phase 1 — Twilio WhatsApp Sandbox Pipeline"
Cohesion: 0.23
Nodes (19): BaseChatModel, ChatOpenAI, main(), get_api_key(), Validate config and ensure data directories exist., validate(), _build_google_llm(), _build_llm() (+11 more)

### Community 9 - "Week 13 Technical Documentation"
Cohesion: 0.14
Nodes (13): 10. Tools, 15. External Services, 17. Error Handling, 19. Design Patterns, 1. Executive Summary, 20. Technology Stack, 26. Request Lifecycle, 27. Example Walkthrough (+5 more)

### Community 10 - "8. LLM Integration"
Cohesion: 0.33
Nodes (6): 8. LLM Integration, Function calling and structured outputs, Output parsing, Prompt templates, Which models are used, Why this split exists

### Community 11 - "29. How I Can Build a Similar Project"
Cohesion: 0.40
Nodes (5): 29. How I Can Build a Similar Project, Domain-specific parts to replace, Generic modules you can reuse, How to adapt it to another Agentic AI app, Reusable architectural ideas

### Community 12 - "Agent Core"
Cohesion: 0.22
Nodes (7): PromptService, Any, Langfuse prompt management with local fallback seeds., Fetch and compile prompts from Langfuse; fall back to local seeds., Prompt service tests., test_local_prompt_fallback_messages(), test_local_prompt_fallback_text()

### Community 13 - "5. Architecture"
Cohesion: 0.29
Nodes (7): 5. Architecture, Component Diagram, Data Flow Diagram, Flow Diagram, Sequence Diagram, Software Architecture, System Architecture

### Community 14 - "8\. Functional Requirements"
Cohesion: 0.33
Nodes (6): 8.1 Agentic Workforce and Conversational Interface, 8.2 Financial and Ticket Management, 8.3 Administrative Dashboard and Agency CRM, 8.5 Marketing and Lead Management, 8.6 Platform Administration and Multi-Tenancy (New), 8\. Functional Requirements

### Community 15 - "14. Configuration"
Cohesion: 0.40
Nodes (5): 14. Configuration, [config/faqs.yaml](config/faqs.yaml), [config/models.yaml](config/models.yaml), [config/param.yaml](config/param.yaml), [.env.example](.env.example)

### Community 16 - "config.py"
Cohesion: 0.10
Nodes (22): get_chat_model(), get_embedding_model(), _get_nested(), get_role_config(), _get_str(), langfuse_configured(), _load_yaml(), Any (+14 more)

### Community 17 - "Tutor_AI_SRS_v2.md"
Cohesion: 0.17
Nodes (11): 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New), 17\. Future Roadmap (Beyond v1), 18\. Glossary, 1.1 The Problem in One Sentence (+3 more)

### Community 18 - "health.py"
Cohesion: 0.12
Nodes (33): BaseModel, Enum, parametrize, active_config(), health(), get, Request, Health, readiness, and config endpoints. (+25 more)

### Community 19 - "test_health.py"
Cohesion: 0.25
Nodes (3): fixture, client(), Phase 0 health endpoint tests.

### Community 20 - "supabase_client.py"
Cohesion: 0.17
Nodes (12): 16.10 V2 Architecture Upgrades (Reference Patterns), 16.11 V2 Acceptance Themes, 16.1 Messaging & Infrastructure, 16.2 AI Agents & Orchestration, 16.3 Memory, Caching & RAG Enhancements, 16.4 Payments & Finance Automation, 16.5 Integrations & Tooling, 16.6 CRM, Dashboard & Backend APIs (Extended) (+4 more)

### Community 21 - "7. Agentic AI Design"
Cohesion: 0.29
Nodes (7): 7. Agentic AI Design, Multi-agent collaboration, Number of agents, Orchestration, Planning and reasoning, Responsibilities, Tool usage

### Community 22 - "Chat Flow"
Cohesion: 0.18
Nodes (11): Retrieval and Ingestion, [src/services/chat_service/cag_cache.py](src/services/chat_service/cag_cache.py), [src/services/chat_service/cag_service.py](src/services/chat_service/cag_service.py), [src/services/chat_service/crag_service.py](src/services/chat_service/crag_service.py), [src/services/chat_service/rag_service.py](src/services/chat_service/rag_service.py), [src/services/chat_service/rag_templates.py](src/services/chat_service/rag_templates.py), [src/services/crm_service/crm_db_client.py](src/services/crm_service/crm_db_client.py), [src/services/crm_service/llm_data_generator.py](src/services/crm_service/llm_data_generator.py) (+3 more)

### Community 23 - "Retrieval and Ingestion"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 24 - "13. APIs"
Cohesion: 0.50
Nodes (4): 13. APIs, Authentication, Errors, Main endpoints

### Community 25 - "16. Execution Flow"
Cohesion: 0.50
Nodes (4): 16. Execution Flow, Application startup, Dependency injection, Request handling

### Community 26 - "2. Overall Project Structure"
Cohesion: 0.50
Nodes (4): 2. Overall Project Structure, Folder Responsibilities, Project Tree, Why the tree is organized this way

### Community 27 - "30. Learning Notes"
Cohesion: 0.50
Nodes (4): 30. Learning Notes, Architecture patterns to recognize, Concepts to study, Interview questions this codebase can inspire

### Community 28 - "4\. Stakeholders and User Roles"
Cohesion: 0.50
Nodes (4): 4.1 User Role Overview, 4.2 Student Profile, 4.3 Tutor and Agency Admin Profile, 4\. Stakeholders and User Roles

### Community 29 - "11. Retrieval"
Cohesion: 0.25
Nodes (8): 11. Retrieval, Chunking, Embeddings, Indexing, Response generation, Retrieved context, Search and ranking, Vector database

### Community 30 - "22. Key Algorithms"
Cohesion: 0.25
Nodes (8): 22. Key Algorithms, Distillation, Guardrail classification, Prompt construction, Retrieval ranking, Routing, Semantic cache lookup, Session warmup

### Community 31 - "9\. Non-Functional Requirements"
Cohesion: 0.25
Nodes (8): 9.1 Usability and Accessibility, 9.2 Performance and Scalability, 9.3 Reliability and Availability, 9.4 Security, 9.5 Data Privacy and Regulatory Compliance, 9.6 Messaging and AI Cost Governance (New), 9.7 Maintainability and Observability, 9\. Non-Functional Requirements

### Community 32 - "21. Dependency Graph"
Cohesion: 0.67
Nodes (3): 21. Dependency Graph, High-level module dependencies, Practical dependency reading order

### Community 33 - "24. Important Functions"
Cohesion: 0.67
Nodes (3): 24. Important Functions, Backend functions that matter most, Frontend functions that matter most

### Community 34 - "9. Memory"
Cohesion: 0.29
Nodes (7): 9. Memory, Conversation history, Long-term semantic memory, Memory lifecycle, Session state, Short-term memory, Vector memory

### Community 35 - "25. Data Models"
Cohesion: 0.67
Nodes (3): 25. Data Models, Backend models, Frontend models

### Community 36 - "12. Database"
Cohesion: 0.33
Nodes (6): 12. Database, Data lifecycle, Database technology, ORM usage, Relationships, Schema areas

### Community 37 - "28. How Everything Connects"
Cohesion: 0.67
Nodes (3): 28. How Everything Connects, Major folder interactions, Visual summary

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
Cohesion: 0.40
Nodes (5): 18. Security, Authentication and authorization, Data access boundaries, Input validation, Secrets

### Community 42 - "3\. Market and Competitive Context"
Cohesion: 0.67
Nodes (3): 3.1 Adjacent Tools and Why They Fall Short, 3.2 Tutor AI's Differentiation, 3\. Market and Competitive Context

### Community 43 - "7\. User Stories"
Cohesion: 0.67
Nodes (3): 7.1 Student and Parent Stories, 7.2 Tutor and Admin Stories (CRM Focused), 7\. User Stories

### Community 56 - "Memory Core"
Cohesion: 0.22
Nodes (9): Memory Core, [src/memory/episodic_store.py](src/memory/episodic_store.py), [src/memory/lt_store.py](src/memory/lt_store.py), [src/memory/memory_ops.py](src/memory/memory_ops.py), [src/memory/policies.py](src/memory/policies.py), [src/memory/procedural_store.py](src/memory/procedural_store.py), [src/memory/prompts.py](src/memory/prompts.py), [src/memory/schemas.py](src/memory/schemas.py) (+1 more)

### Community 59 - "middleware.py"
Cohesion: 0.29
Nodes (5): BaseHTTPMiddleware, Response, Request, Request ID and latency headers., RequestContextMiddleware

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

## Knowledge Gaps
- **314 isolated node(s):** `axiom-ai-backend`, `Quick start (Phase 0)`, `Table of Contents`, `1. Locked Architecture Decisions`, `Model Assignments (Locked for MVP)` (+309 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Week 13 Technical Documentation` connect `Week 13 Technical Documentation` to `Infrastructure Support`, `23. Important Classes`, `3. Folder-by-Folder Explanation`, `Appendix: Complete File Inventory`, `8. LLM Integration`, `29. How I Can Build a Similar Project`, `5. Architecture`, `14. Configuration`, `7. Agentic AI Design`, `13. APIs`, `16. Execution Flow`, `2. Overall Project Structure`, `30. Learning Notes`, `11. Retrieval`, `22. Key Algorithms`, `21. Dependency Graph`, `24. Important Functions`, `9. Memory`, `25. Data Models`, `12. Database`, `28. How Everything Connects`, `18. Security`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `4. File-by-File Explanation` connect `Infrastructure Support` to `Memory Core`, `Week 13 Technical Documentation`, `Tasks`, `Chat Flow`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Why does `23. Important Classes` connect `23. Important Classes` to `Week 13 Technical Documentation`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **What connects `axiom-ai-backend`, `Quick start (Phase 0)`, `Table of Contents` to the rest of the system?**
  _314 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Roadmap.md` be split into smaller, more focused modules?**
  _Cohesion score 0.046511627906976744 - nodes in this community are weakly interconnected._
- **Should `Infrastructure Support` be split into smaller, more focused modules?**
  _Cohesion score 0.05263157894736842 - nodes in this community are weakly interconnected._
- **Should `23. Important Classes` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._