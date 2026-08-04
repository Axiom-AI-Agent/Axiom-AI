Project Planning - AI Tutor SaaS Platform

Objective: To define the project scope, multi-agent architecture, core use cases, and development workflow for an agentic SaaS platform designed to automate operations in the Sri Lankan private tuition sector.

Why It Matters: The shadow education sector handles thousands of students communicating via unstructured WhatsApp and Telegram groups. A well-planned architecture ensures we can handle high message volumes, resolve the Meta Webhook timeout constraints, and efficiently route tasks to specialized agents without inflating LLM token costs.

1\. Requirements Gathering

- Business Domain: Education Technology (SaaS for Sri Lankan Private Tuition/Shadow Education).
- Target User Personas:
  - Students (End-Users): Interact entirely via WhatsApp/Telegram using casual language and phonetic "Singlish".
  - Tutors & Agency Staff (Operations Team): Interact via a Next.js web dashboard (CRM) to view analytics, resolve escalations, and manage ledgers.
- Core User Workflows:
  - Automated Onboarding: Guiding new students through class registration and capturing profile data.
  - Resource Retrieval (RAG): Fetching specific past papers, notes, or recorded lectures from Google Drive based on student queries.
  - Payment Reconciliation: Processing bank slip uploads and verifying them against the ledger.
  - Human Escalation: Identifying complex issues or frustrated sentiment and routing the chat to a human agent's dashboard via SLAs.
- External Data Sources:
  - WhatsApp Business API & Telegram Bot API (Messaging)
  - Supabase (PostgreSQL + pgvector for database and long-term memory)
  - Google Drive (Via Model Context Protocol / MCP for document storage)
  - PayHere API (Payment Gateway)
- LLM Providers:
  - Google Gemini: Native multimodal capabilities make it excellent for parsing handwritten bank slips and processing unstructured "Singlish".
  - Anthropic Claude (Optional/Fallback): Highly effective for complex LangGraph routing and utilizing MCP servers.

2\. Use Case Definition

Case 1: Resource Request (Google Drive MCP)

- User: "Sir, can I get last week's physics paper?"
- Intent → Agent: Resource Request → Resource_Agent
- Tool → Data Source: Google Drive MCP → Google Drive
- Response: Agent retrieves the specific PDF link and sends it to the student.

Case 2: Resource Request (RAG Tool)

- User: "Sir, I cant understand the velocity part of the 5th lesson?"
- Intent → Agent: Resource Request → Resource_Agent
- Tool → Data Source: RAG -> Qdrant
- Response: Agent retrieves the most suitable chunks and gives the response.

Case 2: Payment Verification

- User: \[Uploads an image of a bank transfer slip\] + "Class fee paid."
- Intent → Agent: Payment Submission → Finance_Agent
- Tool → Data Source: Vision Parser / Supabase MCP → Ledger DB
- Response: Agent extracts the transaction ID, updates the Supabase ledger, and sends an automated digital receipt.

Case 3: Student Onboarding

- User: "I want to join the 2026 AL Chemistry class."
- Intent → Agent: Enrollment → Admissions_Agent
- Tool → Data Source: Supabase MCP → Students DB
- Response: Agent asks for index number, school, and district, saving the profile to the database and sending the welcome pack.

Case 4: Human Escalation

- User: "This bot is useless, I need to talk to Sir about my marks!"
- Intent → Agent: Frustration/Escalation → Ticketing_Agent
- Tool → Data Source: Supabase MCP → ESCALATION Table
- Response: Agent apologizes, creates a pending ticket in the CRM, and stops replying to let human staff take over.

Case 5: Routine Admin Query (Semantic Cache Hit)

- User: "Is class postponed today?"
- Intent → Agent: Admin Query → Supervisor_Agent (intercepted by Cache)
- Tool → Data Source: Semantic Cache → Redis/Supabase
- Response: Bypasses LLM entirely; instantly replies "No, class is on schedule at 2 PM" based on a cached answer.

Edge Cases & Error Scenarios

- Meta Webhook Timeout: Meta requires a 200 OK within 3 seconds. The FastAPI layer must immediately queue the payload and respond to Meta _before_ the LangGraph workflow begins to prevent costly retry loops.
- Unreadable Bank Slip: The vision model fails to read the slip. The Finance_Agent must politely ask for a clearer photo or manually escalate it.

3\. Architecture Sketch

User Interfaces:

- Frontend (Students): WhatsApp / Telegram (Invisible UI).
- Frontend (Staff): Next.js Admin CRM Dashboard.

Backend & Orchestration:

- API Layer: FastAPI (handles webhooks, queues payloads, and returns immediate 200 OK responses).
- Background Worker: Pulls messages from the queue and triggers the orchestrator.
- Agent Orchestrator: LangGraph StateGraph acting as the Supervisor.
- Specialist Agents:
  - Admissions_Agent
  - Resource_Agent (RAG equipped)
  - Finance_Agent
  - Ticketing_Agent

Tooling & Memory:

- Tool Layer: MCP Servers isolating Google Drive, Supabase, and PayHere logic.
- Memory System (4 Tiers):
  - Semantic Cache (Bypass LLM for exact match queries).
  - Working Memory (Active LangGraph state).
  - Session Memory (Recent conversation context).
  - Long-Term Memory (Supabase DB with student profiles).
- Database: Supabase (Relational tables for CRM + Vector store for RAG).

\[ALL DIAGRAMS ARE AVAILABLE IN THE DOCS FOLDER\]

4\. Data Flow for a Typical Request

- Ingest: Student sends a WhatsApp message. Meta hits the FastAPI webhook.
- Acknowledge: FastAPI drops the payload into a background queue and instantly fires a 200 OK back to Meta.
- Recall: The background worker picks up the task and checks the Semantic Cache. If it's a miss, it loads the student's profile and chat history from Supabase.
- Route (Fan-Out): The LangGraph Supervisor_Agent analyzes the intent and routes the state to the appropriate specialist (e.g., the Resource_Agent).
- Execute: The Resource_Agent utilizes the Google Drive MCP to search for and retrieve the requested document.
- Merge (Fan-In): The agent formats the final response and returns it to the main LangGraph state.
- Save & Respond: The system saves the interaction to the chat_logs table, updates memory, and sends the final message back to the student via the Meta Cloud API.