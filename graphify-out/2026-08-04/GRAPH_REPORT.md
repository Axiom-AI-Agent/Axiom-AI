# Graph Report - Axiom-AI  (2026-08-04)

## Corpus Check
- 5 files · ~354,231 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 350 nodes · 345 edges · 27 communities (26 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b42d0fdc`
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
- Tutor_AI_SRS_v2.md
- Chat Flow
- Retrieval and Ingestion
- 11. Retrieval
- 22. Key Algorithms
- 9\. Non-Functional Requirements
- 7. Agentic AI Design
- 9. Memory
- 12. Database
- 6\. User Journeys
- 18. Security
- 13. APIs
- 2. Overall Project Structure
- README.md

## God Nodes (most connected - your core abstractions)
1. `Week 13 Technical Documentation` - 34 edges
2. `23. Important Classes` - 18 edges
3. `3. Folder-by-Folder Explanation` - 16 edges
4. `Axiom AI — AI Backend Roadmap` - 15 edges
5. `Appendix: Complete File Inventory` - 15 edges
6. `Infrastructure Support` - 14 edges
7. `Chat Flow` - 11 edges
8. `Retrieval and Ingestion` - 11 edges
9. `Agent Core` - 10 edges
10. `Memory Core` - 9 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities (27 total, 1 thin omitted)

### Community 0 - "Roadmap.md"
Cohesion: 0.06
Nodes (35): 7. Phased Implementation Plan, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Acceptance Criteria, Deliverables (+27 more)

### Community 1 - "Infrastructure Support"
Cohesion: 0.07
Nodes (27): 4. File-by-File Explanation, Agent Core, Backend Entry and Transport, MCP Servers, [src/agents/decision_graph.py](src/agents/decision_graph.py), [src/agents/guardrail.py](src/agents/guardrail.py), [src/agents/orchestrator.py](src/agents/orchestrator.py), [src/agents/prompts/agent_prompts.py](src/agents/prompts/agent_prompts.py) (+19 more)

### Community 2 - "23. Important Classes"
Cohesion: 0.11
Nodes (18): 23. Important Classes, [src/agents/guardrail.py](src/agents/guardrail.py), [src/agents/orchestrator.py](src/agents/orchestrator.py), [src/agents/router.py](src/agents/router.py), [src/memory/memory_ops.py](src/memory/memory_ops.py), [src/memory/schemas.py](src/memory/schemas.py), [src/services/chat_service/cag_cache.py](src/services/chat_service/cag_cache.py), [src/services/chat_service/cag_service.py](src/services/chat_service/cag_service.py) (+10 more)

### Community 3 - "Tasks"
Cohesion: 0.08
Nodes (25): 10. Explicitly Out of MVP Scope, 11. Per-Phase Workflow, 12. Day-by-Day Schedule, 1. Locked Architecture Decisions, 2. System Understanding, 3. Resource Split: Google Drive vs RAG, 4. Multi-Tenant Data Model, 5. Reference Patterns to Reuse (+17 more)

### Community 4 - "Tasks"
Cohesion: 0.14
Nodes (14): Infrastructure Support, [src/infrastructure/config.py](src/infrastructure/config.py), [src/infrastructure/db/crm_init.py](src/infrastructure/db/crm_init.py), [src/infrastructure/db/crm_models.py](src/infrastructure/db/crm_models.py), [src/infrastructure/db/qdrant_client.py](src/infrastructure/db/qdrant_client.py), [src/infrastructure/db/sql_client.py](src/infrastructure/db/sql_client.py), [src/infrastructure/db/supabase_client.py](src/infrastructure/db/supabase_client.py), [src/infrastructure/db/supabase_schema.py](src/infrastructure/db/supabase_schema.py) (+6 more)

### Community 5 - "3. Folder-by-Folder Explanation"
Cohesion: 0.12
Nodes (16): 3. Folder-by-Folder Explanation, [config](config), [docker](docker), [notebooks](notebooks), Root Files, [scripts](scripts), [sql](sql), [src/agents](src/agents) (+8 more)

### Community 6 - "Tasks"
Cohesion: 0.22
Nodes (9): Memory Core, [src/memory/episodic_store.py](src/memory/episodic_store.py), [src/memory/lt_store.py](src/memory/lt_store.py), [src/memory/memory_ops.py](src/memory/memory_ops.py), [src/memory/policies.py](src/memory/policies.py), [src/memory/procedural_store.py](src/memory/procedural_store.py), [src/memory/prompts.py](src/memory/prompts.py), [src/memory/schemas.py](src/memory/schemas.py) (+1 more)

### Community 7 - "Appendix: Complete File Inventory"
Cohesion: 0.13
Nodes (15): Appendix: Complete File Inventory, config, docker, notebooks, Root, scripts, sql, src/agents (+7 more)

### Community 8 - "Phase 1 — Twilio WhatsApp Sandbox Pipeline"
Cohesion: 0.25
Nodes (8): Acceptance Criteria, Deliverables, Dependencies, Features, Files / Modules, Objective, Phase 1 — Twilio WhatsApp Sandbox Pipeline, Risks

### Community 9 - "Week 13 Technical Documentation"
Cohesion: 0.04
Nodes (45): 10. Tools, 14. Configuration, 15. External Services, 16. Execution Flow, 17. Error Handling, 19. Design Patterns, 1. Executive Summary, 20. Technology Stack (+37 more)

### Community 10 - "8. LLM Integration"
Cohesion: 0.33
Nodes (6): 8. LLM Integration, Function calling and structured outputs, Output parsing, Prompt templates, Which models are used, Why this split exists

### Community 11 - "29. How I Can Build a Similar Project"
Cohesion: 0.40
Nodes (5): 29. How I Can Build a Similar Project, Domain-specific parts to replace, Generic modules you can reuse, How to adapt it to another Agentic AI app, Reusable architectural ideas

### Community 17 - "Tutor_AI_SRS_v2.md"
Cohesion: 0.05
Nodes (36): 10.1 Agent Roster, 10.2 Conceptual Data Flow, 10\. System Architecture Overview (High Level), 11\. Data Model - Key Entities, 12\. Third-Party Integrations and Technical Constraints, 13\. Risk Register, 14\. Monetisation and SaaS Pricing Model (New), 15\. Success Metrics / KPIs (New) (+28 more)

### Community 22 - "Chat Flow"
Cohesion: 0.18
Nodes (11): Chat Flow, [src/api/routers/chat.py](src/api/routers/chat.py), [src/api/routers/chat_sessions.py](src/api/routers/chat_sessions.py), [src/api/routers/health.py](src/api/routers/health.py), [src/api/routers/patients.py](src/api/routers/patients.py), [src/api/routers/tools/cag.py](src/api/routers/tools/cag.py), [src/api/routers/tools/crawl.py](src/api/routers/tools/crawl.py), [src/api/routers/tools/crm.py](src/api/routers/tools/crm.py) (+3 more)

### Community 23 - "Retrieval and Ingestion"
Cohesion: 0.18
Nodes (11): Retrieval and Ingestion, [src/services/chat_service/cag_cache.py](src/services/chat_service/cag_cache.py), [src/services/chat_service/cag_service.py](src/services/chat_service/cag_service.py), [src/services/chat_service/crag_service.py](src/services/chat_service/crag_service.py), [src/services/chat_service/rag_service.py](src/services/chat_service/rag_service.py), [src/services/chat_service/rag_templates.py](src/services/chat_service/rag_templates.py), [src/services/crm_service/crm_db_client.py](src/services/crm_service/crm_db_client.py), [src/services/crm_service/llm_data_generator.py](src/services/crm_service/llm_data_generator.py) (+3 more)

### Community 29 - "11. Retrieval"
Cohesion: 0.25
Nodes (8): 11. Retrieval, Chunking, Embeddings, Indexing, Response generation, Retrieved context, Search and ranking, Vector database

### Community 30 - "22. Key Algorithms"
Cohesion: 0.25
Nodes (8): 22. Key Algorithms, Distillation, Guardrail classification, Prompt construction, Retrieval ranking, Routing, Semantic cache lookup, Session warmup

### Community 31 - "9\. Non-Functional Requirements"
Cohesion: 0.25
Nodes (8): 9.1 Usability and Accessibility, 9.2 Performance and Scalability, 9.3 Reliability and Availability, 9.4 Security, 9.5 Data Privacy and Regulatory Compliance, 9.6 Messaging and AI Cost Governance (New), 9.7 Maintainability and Observability, 9\. Non-Functional Requirements

### Community 33 - "7. Agentic AI Design"
Cohesion: 0.29
Nodes (7): 7. Agentic AI Design, Multi-agent collaboration, Number of agents, Orchestration, Planning and reasoning, Responsibilities, Tool usage

### Community 34 - "9. Memory"
Cohesion: 0.29
Nodes (7): 9. Memory, Conversation history, Long-term semantic memory, Memory lifecycle, Session state, Short-term memory, Vector memory

### Community 36 - "12. Database"
Cohesion: 0.33
Nodes (6): 12. Database, Data lifecycle, Database technology, ORM usage, Relationships, Schema areas

### Community 38 - "6\. User Journeys"
Cohesion: 0.33
Nodes (6): 6.1 Student Journey - Registration and Daily Operations, 6.2 Financial Journey - Payment Collection, 6.3 Attendance Journey (New), 6.4 Admin / Agency Journey - CRM and Dashboard Management, 6.5 Tutor Onboarding Journey (New), 6\. User Journeys

### Community 41 - "18. Security"
Cohesion: 0.40
Nodes (5): 18. Security, Authentication and authorization, Data access boundaries, Input validation, Secrets

### Community 43 - "13. APIs"
Cohesion: 0.50
Nodes (4): 13. APIs, Authentication, Errors, Main endpoints

### Community 45 - "2. Overall Project Structure"
Cohesion: 0.50
Nodes (4): 2. Overall Project Structure, Folder Responsibilities, Project Tree, Why the tree is organized this way

## Knowledge Gaps
- **290 isolated node(s):** `Axiom-AI`, `Table of Contents`, `1. Locked Architecture Decisions`, `Business Problem`, `MVP Solution (AI Backend)` (+285 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Week 13 Technical Documentation` connect `Week 13 Technical Documentation` to `Infrastructure Support`, `23. Important Classes`, `7. Agentic AI Design`, `12. Database`, `3. Folder-by-Folder Explanation`, `9. Memory`, `Appendix: Complete File Inventory`, `18. Security`, `8. LLM Integration`, `13. APIs`, `29. How I Can Build a Similar Project`, `2. Overall Project Structure`, `11. Retrieval`, `22. Key Algorithms`?**
  _High betweenness centrality (0.367) - this node is a cross-community bridge._
- **Why does `4. File-by-File Explanation` connect `Infrastructure Support` to `Tasks`, `Tasks`, `Week 13 Technical Documentation`, `Chat Flow`, `Retrieval and Ingestion`?**
  _High betweenness centrality (0.217) - this node is a cross-community bridge._
- **Why does `23. Important Classes` connect `23. Important Classes` to `Week 13 Technical Documentation`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **What connects `Axiom-AI`, `Table of Contents`, `1. Locked Architecture Decisions` to the rest of the system?**
  _290 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Roadmap.md` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `Infrastructure Support` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._
- **Should `23. Important Classes` be split into smaller, more focused modules?**
  _Cohesion score 0.1111111111111111 - nodes in this community are weakly interconnected._