**AXIOM AI**

Software Requirements Specification

_A Multi-Agent, Agentic SaaS Platform for the Sri Lankan Private Tuition Sector_

July 2026

| **Field**             | **Detail**                                            |
| --------------------- | ----------------------------------------------------- |
| Document Status       | Draft for Review - v2.0                               |
| Prepared For          | AXIOM AI Founding Team                                |
| Primary Market        | Sri Lanka - Private Tuition / Shadow Education Sector |
| Distribution Channels | WhatsApp Business API, Telegram Bot API               |
| Supersedes            | Tutor AI SRS v1.0 (initial draft)                     |

# 1\. Executive Summary

Tutor AI is a multi-agent, SaaS-based digital platform for Education Sector. It replaces the chaotic manual management of WhatsApp and Telegram groups with an intelligent agentic platform that gives students instant access to resources, automates fee collection and reconciliation, and gives tuition agencies a centralised operational dashboard and CRM.

## 1.1 The Problem in One Sentence

Sri Lanka's private tuition industry - from solo home-based teachers to mass-education sectors with thousands of students - is run largely through unstructured WhatsApp/Telegram groups, and the resulting flood of repetitive questions, manual payment reconciliation, and ungraded papers overwhelms tutors and their small admin teams.

# 2\. Purpose, Scope, and Definitions

## 2.1 Purpose

This document defines the problem Tutor AI solves, the stakeholders it serves, their user journeys, and the functional and non-functional requirements the system must satisfy, including the Management CRM/Dashboard and the platform-level (multi-tenant) administration layer needed to run Tutor AI as a SaaS business.

## 2.2 In Scope / Out of Scope

| **In Scope**                                                             | **Out of Scope (v1 product)**                                                     |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| Conversational AI via WhatsApp and Telegram                              | Native mobile app for students or tutors                                          |
| Automated RAG-based Q&A and doubt clearance                              | Full Learning Management System (LMS) web portal                                  |
| Payment collection, bank-slip OCR verification, and fraud checks         | Video hosting / live-streaming infrastructure for lectures                        |
| MCQ grading via vision models                                            | Automated essay / structured-answer grading                                       |
| Agency CRM, escalation inbox, and Management Dashboard                   | Student loan or instalment financing                                              |
| Multi-tenant platform administration and subscription billing for tutors | Federated multi-branch/multi-hospital-style enterprise management                 |
| Sri Lanka PDPA-aligned data handling                                     | Full GDPR certification for EU expansion (tracked as a future consideration only) |

# 3\. Market and Competitive Context

This section was added after research into the local messaging-commerce and ed-tech landscape, to sharpen why Tutor AI is differentiated rather than a thin wrapper around a chatbot builder.

## 3.1 Adjacent Tools and Why They Fall Short

| **Category**                            | **Examples**                          | **Gap for Sri Lankan Tuition**                                                                                                                                                                |
| --------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Generic WhatsApp CRM / chatbot builders | WATI, SleekFlow, Twilio-based tools   | Built for e-commerce support flows; no concept of a class, a term fee, a bank-slip receipt, an MCQ answer sheet, or a seat ticket. Tutors would still hand-build all the logic.               |
| Traditional LMS                         | Moodle, Google Classroom              | Requires a dedicated app/portal and login - the opposite of "invisible technology." Sri Lankan students and parents already live in WhatsApp/Telegram; a second destination reduces adoption. |
| Manual group admins / paper markers     | Human staff hired by top tutors       | Does the job Tutor AI automates, but scales linearly with cost and cannot operate at 2 a.m. when students study.                                                                              |
| Local payment-only tools                | PayHere plugins, manual bank transfer | Handle the money but not the reconciliation-to-student-record step, which is the actual bottleneck (see FR-FI-02).                                                                            |

## 3.2 Tutor AI's Differentiation

- Local-language, local-behaviour NLP: Singlish, Sinhala/Tamil voice notes, and late-night informal phrasing, not just English intents.
- Payment reconciliation is treated as a first-class workflow (OCR bank-slip matching + PayHere), not a bolt-on.
- Designed to scale from a single independent tutor to a multi-staff agency without switching products - the CRM and escalation layer is what a growing agency needs next.

# 4\. Stakeholders and User Roles

## 4.1 User Role Overview

| **Role**                             | **Who They Are**                                                        | **What They Do in Tutor AI**                                                                                                            |
| ------------------------------------ | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Student                              | A learner enrolled in a class.                                          | Interacts with the AI via WhatsApp/Telegram to register, ask questions, retrieve notes, submit MCQ answers, and check in for class.     |
| Parent / Guardian                    | The financial sponsor of the student.                                   | Receives automated progress reports and payment reminders via WhatsApp; can be linked to multiple children.                             |
| Independent Tutor                    | A solo teacher managing a class.                                        | Uses the AI to save time on manual replies and payment links; the primary decision-maker and billing contact for a small tenant.        |
| Agency Admin / Staff                 | Employees of top-tier teachers (paper markers, chat admins, marketers). | Uses the CRM/Dashboard to manage escalations, reconcile bulk payments, review analytics, and route paper-marking.                       |
| Junior Paper Marker                  | Staff member assigned to grade a subset of submissions.                 | Receives auto-routed assignment photos filtered by district/class and records marks.                                                    |
| Platform Super Admin (Tutor AI team) | Tutor AI's own operations/support staff.                                | Onboards new tutor tenants, manages subscription billing, monitors platform health, and handles cross-tenant support (see Section 8.8). |

## 4.2 Student Profile

Students are highly active on mobile devices and rely heavily on WhatsApp and Telegram. They often type in "Singlish" (phonetic Sinhala using the English alphabet) or send rapid-fire voice notes rather than formal English text. They frequently study late at night and need 24/7 academic support when their human tutors are asleep.

## 4.3 Tutor and Agency Admin Profile

Top-tier tutors operate more like business executives than solo educators: they manage large student databases and run targeted ad campaigns to generate leads. Agency admins face high cognitive load from manual fee reconciliation, repetitive queries, and grading. They need a dashboard usable on a tablet, not a raw chat log, to manage the business.

# 5\. Problem Definition

## 5.1 Current State (Without Tutor AI)

Teachers manage hundreds of students via chaotic WhatsApp or Telegram groups: manually adding numbers to crowded groups, scrolling back to resend PDFs to late joiners, and running physical entry at the door as a logistical exercise of checking printed ID cards. Students studying late at night get stuck on a problem while the tutor is asleep, and momentum is lost.

# 6\. User Journeys

## 6.1 Student Journey - Registration and Daily Operations

| **Step** | **Stage**          | **What Happens**                                                                                                                                              |
| -------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1        | Onboarding         | The student texts "Join Science 2026"; the Admissions Agent registers them automatically.                                                                     |
| 2        | Data collection    | The agent asks for the student's name, school, and district, registers them in the database, and sends the introductory syllabus and class rules.             |
| 3        | Material retrieval | If the student asks "I missed last week's class, what did we do?", the Resource (RAG) Agent finds and sends the relevant PDF notes and recorded-lecture link. |
| 4        | Doubt clearance    | At night, the student asks a question; the Academic Assistant Agent guides them step-by-step using the tutor's own teaching methodology.                      |

## 6.2 Financial Journey - Payment Collection

| **Step** | **Stage**              | **What Happens**                                                                                                                                                                                                         |
| -------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1        | Reminders              | The Finance & Ledger Agent tracks who has paid this month and issues automated reminders, preferring free service-window messages over paid templates.                                                                   |
| 2        | Payment submission     | The student pays via PayHere (card, bank app, or e-wallet) or uploads a photo of a bank transfer slip.                                                                                                                   |
| 3        | Automated verification | The Finance Agent uses OCR to read the slip, extract the amount, date, and reference, cross-checks it against bank statement data where available, and flags duplicates or mismatches instead of auto-approving blindly. |
| 5        | Dispute handling       | If a slip is flagged as suspicious or a parent disputes a charge, the case routes to the Escalation Inbox for human review rather than auto-resolving (see FR-FI-05).                                                    |

## 6.3 Attendance Journey (New)

| **Step** | **Stage**         | **What Happens**                                                                                                                   |
| -------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| 1        | Check-in          | On arrival, the student shows or scans their monthly QR ticket; the Ticketing Agent logs a timestamped attendance record.          |
| 2        | Absence follow-up | If a paid student misses class, the system can optionally notify the parent and log the absence for the tutor's at-risk dashboard. |
| 3        | Reporting         | Attendance rolls up into the monthly parent progress report and the CRM's student 360-degree view.                                 |

## 6.4 Admin / Agency Journey - CRM and Dashboard Management

| **Step** | **Stage**           | **What Happens**                                                                                                                                          |
| -------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1        | Dashboard view      | Staff log in and see real-time statistics on how many students have paid this month.                                                                      |
| 2        | FAQ monitoring      | Staff review the most frequently asked questions (e.g. 500 students asking "Is the exam postponed?") so the tutor can issue a single mass announcement.   |
| 3        | Escalation handling | Staff manage the Escalation Inbox where the AI routes complex, angry, or highly specific messages, each tagged with an urgency level and an SLA timer.    |
| 5        | Fraud review        | Staff review payment-verification flags raised by the Finance Agent (duplicate slips, amount mismatches) before funds are credited to a student's record. |

## 6.5 Tutor Onboarding Journey (New)

A new tutor signs up on Tutor AI's website or is onboarded by the Platform Super Admin team, connects a WhatsApp Business number (via an approved Business Solution Provider) and/or Telegram bot, links a Google Drive folder of teaching resources, configures classes and fee amounts through a guided setup wizard, and goes live - without writing any code or manually training a chatbot from scratch.

# 7\. User Stories

## 7.1 Student and Parent Stories

| **ID** | **As a...** | **I want to...**                                                        | **So that...**                                                       | **Priority** |
| ------ | ----------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------ |
| US-S01 | student     | send voice notes in Sinhala or Tamil                                    | the AI transcribes, translates, and replies in my preferred language | Must Have    |
| US-S02 | student     | photograph my filled MCQ answer sheet and send it via WhatsApp          | the AI grades it instantly against the master answer key             | Must Have    |
| US-S03 | student     | ask questions at night and be guided step-by-step                       | I can keep studying using my tutor's own teaching method             | Must Have    |
| US-S04 | student     | check my own attendance and payment status on request                   | I don't have to ask a human admin                                    | Should Have  |
| US-P01 | parent      | have my WhatsApp number collected alongside the student's at onboarding | I'm kept in the loop                                                 | Must Have    |
| US-P02 | parent      | receive a personalised, visually appealing monthly progress report      | I can see attendance, fee status, and exam scores in one place       | Must Have    |
| US-P03 | parent      | link more than one child under my account                               | I get one combined view instead of juggling separate threads         | Should Have  |

## 7.2 Tutor and Admin Stories (CRM Focused)

| **ID** | **As a...**        | **I want to...**                                                        | **So that...**                                                        | **Priority** |
| ------ | ------------------ | ----------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------ |
| US-A01 | high-level teacher | capture leads directly from Facebook/Instagram ads                      | a click-to-WhatsApp ad automatically registers a lead into my CRM     | Should Have  |
| US-A02 | admin              | have the AI route student queries to specific human departments         | staff can handle escalations efficiently from the dashboard           | Must Have    |
| US-A03 | tutor              | assign seat numbers on a "first to pay, best seat" basis                | the door-rush chaos is eliminated                                     | Could Have   |
| US-A04 | admin              | view a consolidated student profile (payments, attendance, exam scores) | I have full context if I need to take over a conversation from the AI | Must Have    |
| US-A05 | admin              | be alerted automatically when a bank slip looks duplicated or forged    | I don't credit a payment that never actually happened                 | Must Have    |
| US-A06 | tutor              | set a monthly WhatsApp messaging budget and see spend in real time      | I never get an unexpected Meta bill                                   | Should Have  |
| US-A07 | agency admin       | assign staff roles with different dashboard permissions                 | junior paper markers can't see financial data they don't need         | Should Have  |
| US-A08 | tutor              | get a self-serve onboarding wizard                                      | I can launch without hiring a developer                               | Must Have    |

# 8\. Functional Requirements

Requirements are grouped by module. Priority follows MoSCoW (Must / Should / Could / Won't have this release).

## 8.1 Agentic Workforce and Conversational Interface

| **ID**   | **Requirement**                                                                                                                                                                                        | **Priority** |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| FR-AI-01 | The system must use a platform-agnostic multi-agent backend that plugs into both the WhatsApp Business API (via an approved Business Solution Provider) and the Telegram Bot API.                      | Must Have    |
| FR-AI-02 | The system must use NLP to decipher phonetic Sinhala/Tamil ("Singlish"), and audio voice notes, understand intent, and reply accurately in the student's preferred language.                           | Must Have    |
| FR-AI-03 | The Resource (RAG) Agent must use Retrieval-Augmented Generation to search the tutor's connected Google Drive, find the exact document, and send it in-chat.                                           | Must Have    |
| FR-AI-04 | The Academic Assistant Agent must be grounded in the tutor's own past-paper discussions and lesson transcripts to act as a 24/7 study buddy in the tutor's teaching style.                             | Must Have    |
| FR-AI-05 | The system must use vision models to grade photographed MCQ answer sheets against a master answer key and log the score.                                                                               | Must Have    |
| FR-AI-06 | The system must detect low-confidence or out-of-scope answers and hand the conversation to a human via the Escalation Inbox rather than guessing.                                                      | Must Have    |
| FR-AI-07 | The system must let a human admin correct an AI answer after the fact and feed that correction back so the same mistake is less likely to repeat.                                                      | Should Have  |
| FR-AI-08 | The system must prefer replying within an open, user-initiated free messaging window and defer non-urgent tutor-initiated messages until such a window is open or a low-cost utility template applies. | Should Have  |

## 8.2 Financial and Ticket Management

| **ID**   | **Requirement**                                                                                                                                                                                                                           | **Priority** |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| FR-FI-01 | The Finance Agent must securely handle monthly class fee collection, track which student has paid, and send automated receipts.                                                                                                           | Must Have    |
| FR-FI-02 | The system must use OCR to read uploaded bank-slip images, verify the amount and date, and automatically tick the corresponding student off the paid list.                                                                                | Must Have    |
| FR-FI-03 | The Ticketing Agent must generate a dynamic QR code for the month and send it via WhatsApp once a student's payment is confirmed.                                                                                                         | Must Have    |
| FR-FI-04 | The system must flag a bank slip as suspicious - and route it to human review instead of auto-approving - when it detects a duplicate image hash, a mismatched amount, an edited-looking image, or a slip reused for a different student. | Must Have    |

## 8.3 Administrative Dashboard and Agency CRM

| **ID**   | **Requirement**                                                                                                                                                                             | **Priority** |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| FR-AD-01 | The Administrative Supervisor Agent must provide an escalation inbox that routes complex, angry, or highly specific messages requiring human intervention, tagged with an urgency level.    | Must Have    |
| FR-AD-02 | The Assignment Routing Agent must automatically log photos of completed assignments, categorise them by district/class, and forward them to the assigned junior paper-marker's dashboard.   | Must Have    |
| FR-AD-03 | The system must flag frequently asked questions (e.g. 500 students asking "Is the exam postponed?") so the tutor can issue one mass announcement instead of hundreds of individual replies. | Must Have    |
| FR-AD-04 | The CRM must provide a 360-degree view of every student: attendance, OCR/PayHere payment history, exam scores, escalation history, and tagged lead source.                                  | Must Have    |
| FR-AD-05 | The CRM must support role-based access control so staff (e.g. junior paper markers) see only the data relevant to their role, while admins see everything.                                  | Should Have  |
| FR-AD-06 | The CRM must let an admin take over a live conversation from the AI at any time, with the full chat history visible, and hand it back afterward.                                            | Must Have    |
| FR-AD-07 | Escalations must carry a configurable SLA timer, and the dashboard must visually flag escalations approaching or past their SLA.                                                            | Should Have  |
| FR-AD-08 | The system must let an admin send a single mass-announcement message that is deduplicated against recent broadcasts to avoid spamming the same student twice.                               | Should Have  |
| FR-AD-09 | The dashboard must be usable on a tablet, not only desktop (see NFR-US-03).                                                                                                                 | Must Have    |

## 8.5 Marketing and Lead Management

| **ID**   | **Requirement**                                                                                                                                                                            | **Priority** |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------ |
| FR-MK-01 | The system must support click-to-WhatsApp ad entry points so a lead who clicks a Facebook/Instagram ad is automatically captured and tagged in the CRM.                                    | Should Have  |
| FR-MK-02 | The system must track lead source and conversion status (lead → registered → paying student) for basic funnel analytics.                                                                   | Should Have  |
| FR-MK-03 | The system must let a tutor design a simple automated nurture sequence for leads who register interest but don't complete enrolment, respecting WhatsApp's free-window and template rules. | Could Have   |
|          |                                                                                                                                                                                            |              |

## 8.6 Platform Administration and Multi-Tenancy (New)

Tutor AI is itself a SaaS product serving many independent tutors and agencies ("tenants"). This module was not explicit in the original draft but is required for the product to operate as a business rather than a single custom deployment.

| **ID**   | **Requirement**                                                                                                                                                 | **Priority** |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| FR-PL-01 | The system must isolate each tutor's data (students, resources, payments, conversations) from every other tutor's data at the database and application layer.   | Must Have    |
| FR-PL-02 | The system must provide a guided, self-serve onboarding wizard for a new tutor to connect WhatsApp/Telegram, link Google Drive, and configure classes and fees. | Must Have    |
| FR-PL-03 | The system must meter usage per tenant (messages sent, OCR calls, LLM tokens, active students) to support both cost control and tiered billing.                 | Must Have    |
| FR-PL-04 | The system must let the Platform Super Admin suspend, migrate, or offboard a tenant, including a data-export function for the tutor's own records.              | Must Have    |
| FR-PL-05 | The system must support subscription billing for tutors (see Section 14) including plan upgrades/downgrades and usage-based overage charges.                    | Should Have  |
| FR-PL-06 | The system must provide a status page / health dashboard for the Platform Super Admin covering all tenants' message delivery rates and error rates.             | Should Have  |

# 9\. Non-Functional Requirements

## 9.1 Usability and Accessibility

| **ID**    | **Requirement**                                                                                                                                 | **Priority** |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| NFR-US-01 | The technology must be invisible to the end user; students and tutors should never need to download a new app or learn a complicated dashboard. | Must Have    |
| NFR-US-02 | The system must support interactions where users send voice notes in Sinhala or Tamil.                                                          | Must Have    |
| NFR-US-03 | The CRM dashboard must be responsive and fully functional on a tablet interface for agency staff.                                               | Must Have    |
| NFR-US-04 | The dashboard UI must itself be available in English, Sinhala, and Tamil for agency staff.                                                      | Should Have  |

## 9.2 Performance and Scalability

| **ID**    | **Requirement**                                                                                                                                                                                                  | **Priority** |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| NFR-SC-01 | The system must scale across thousands of tutors and handle mass lecture classes that may attract hundreds or thousands of students each.                                                                        | Must Have    |
| NFR-SC-02 | AI models used (e.g. large-context Gemini or Claude-class models) must support large context windows to hold entire syllabi and lesson transcripts.                                                              | Must Have    |
| NFR-SC-03 | The system must handle predictable seasonal surges (e.g. exam-result days, fee due-dates, MCQ submission windows right after a mass class) without degraded response time.                                       | Must Have    |
| NFR-SC-04 | Median chatbot response latency for a student query must stay under roughly 5 seconds under normal load; heavier operations such as MCQ vision grading may take longer but must acknowledge receipt immediately. | Should Have  |

## 9.3 Reliability and Availability

| **ID**    | **Requirement**                                                                                                                                                            | **Priority** |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| NFR-RE-01 | Core messaging and payment-webhook endpoints must target at least 99.5% uptime.                                                                                            | Must Have    |
| NFR-RE-02 | If the WhatsApp or Telegram API is temporarily unavailable, inbound and outbound messages must queue and retry rather than being silently dropped.                         | Must Have    |
| NFR-RE-03 | The system must maintain automated backups of all tenant data with a defined recovery point objective (RPO) and recovery time objective (RTO), documented per tenant tier. | Should Have  |
| NFR-RE-04 | If a tutor's WhatsApp number is restricted or banned by Meta, the system must support failover to Telegram as a communication channel with minimal disruption.             | Should Have  |

## 9.4 Security

| **ID**    | **Requirement**                                                                                                                                                                    | **Priority** |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| NFR-SE-01 | All payment notifications (PayHere webhooks) must be checksum-verified server-side before any balance is updated; a payment must never be trusted from client-supplied data alone. | Must Have    |
| NFR-SE-02 | All data in transit must use TLS; sensitive data at rest (payment references, personal data) must be encrypted.                                                                    | Must Have    |
| NFR-SE-03 | Admin and staff accounts must support role-based access control and, for financial actions, an audit log of who did what and when.                                                 | Must Have    |
| NFR-SE-04 | The platform must never store full card numbers or CVVs; card data is handled exclusively by PCI-DSS-compliant processors (PayHere).                                               | Must Have    |
| NFR-SE-05 | The system must rate-limit and monitor for abuse patterns (e.g. one student flooding the AI with requests to run up a tutor's messaging costs).                                    | Should Have  |

## 9.5 Data Privacy and Regulatory Compliance

Sri Lanka's Personal Data Protection Act, No. 9 of 2022 (PDPA), as amended in 2025, establishes the Data Protection Authority of Sri Lanka and is expected to bring its substantive provisions (lawful processing, data-subject rights, security obligations, cross-border transfer rules, and penalties of up to LKR 10 million per instance of non-compliance) into force during 2026. Tutor AI processes student and parent personal data - including, potentially, minors' data - at scale, so PDPA alignment is a Must Have, not a future consideration.

| **ID**    | **Requirement**                                                                                                                                                                                                                    | **Priority** |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| NFR-PR-01 | The system must capture explicit, recorded consent from a parent/guardian (or an adult student) before enrolling them into automated WhatsApp/Telegram messaging, and must provide an opt-out.                                     | Must Have    |
| NFR-PR-02 | The system must support data-subject rights required under the PDPA: access to one's own data, correction, and deletion/withdrawal of consent, initiated through the tutor's admin or directly by the data subject.                | Must Have    |
| NFR-PR-03 | The system must apply data minimisation: collect only the fields actually needed (name, school, district, contact, payment reference) and avoid collecting sensitive categories (e.g. religion, health) unless strictly necessary. | Must Have    |
| NFR-PR-04 | Financial transaction records must be retained for the period required by Sri Lankan tax law (commonly cited as around 7 years), while conversational/chat data should have a shorter, configurable retention period.              | Should Have  |
| NFR-PR-05 | If any tenant data is processed or stored on servers outside Sri Lanka, the platform must apply the safeguards the PDPA requires for cross-border transfer.                                                                        | Should Have  |
| NFR-PR-06 | The platform must maintain a Data Protection Management Programme (internal controls, breach-notification process) proportionate to its scale, in anticipation of PDPA enforcement.                                                | Should Have  |

_Note: As of mid-2026, most PDPA substantive provisions are not yet fully in force, but the Data Protection Authority is active and provisions are expected to be operationalised through 2026. Building compliant data handling in from day one avoids a costly retrofit and is good practice regardless of the exact enforcement date. This is not legal advice - confirm current PDPA status with a Sri Lankan legal advisor before launch._

## 9.6 Messaging and AI Cost Governance (New)

Because Meta now bills WhatsApp template messages per delivery (varying by category and recipient country) rather than per 24-hour conversation, and because LLM/vision-model inference has a real per-call cost, Tutor AI's own unit economics depend on disciplined cost governance.

| **ID**    | **Requirement**                                                                                                                                                                                                  | **Priority** |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| NFR-CO-01 | The system must default to replying inside free, user-initiated service windows and use low-cost "utility" templates for transactional outreach (payment reminders, receipts) rather than "marketing" templates. | Must Have    |
| NFR-CO-02 | The system must let each tutor set a monthly messaging and AI-usage budget, with alerts as spend approaches the cap.                                                                                             | Should Have  |
| NFR-CO-03 | The system must track per-tenant cost (messaging + LLM + OCR + vision grading) to inform pricing tiers and detect anomalous usage.                                                                               | Must Have    |
| NFR-CO-04 | The system must batch or defer non-urgent broadcast messages to control per-message spend during peak periods (e.g. exam announcement day).                                                                      | Could Have   |

## 9.7 Maintainability and Observability

| **ID**    | **Requirement**                                                                                                                                                              | **Priority** |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| NFR-MO-01 | All agent actions (auto-replies, payment approvals, grading results) must be logged with enough detail to reconstruct what happened and why, for support and audit purposes. | Must Have    |
| NFR-MO-02 | The platform must expose monitoring/alerting on message delivery failures, webhook failures, and AI error rates.                                                             | Should Have  |
| NFR-MO-03 | Prompt/agent configuration should be updatable per tenant without a full redeploy, so a tutor's teaching style or fee rules can change without engineering involvement.      | Should Have  |

# 10\. System Architecture Overview (High Level)

This is a requirements-level view, not a technical design document; it exists to make the agent boundaries and data flow explicit enough for engineering to scope work.

## 10.1 Agent Roster

| **Agent**                       | **Responsibility**                                                                                  |
| ------------------------------- | --------------------------------------------------------------------------------------------------- |
| Admissions Agent                | Handles new-student registration, onboarding questions, and PDPA consent capture.                   |
| Resource (RAG) Agent            | Retrieves PDFs, notes, and recorded-lecture links from the tutor's connected Google Drive.          |
| Academic Assistant Agent        | Provides step-by-step doubt clearance grounded in the tutor's own materials and methodology.        |
| Grading Agent                   | Uses vision models to grade photographed MCQ sheets against a master answer key.                    |
| Finance & Ledger Agent          | Tracks fee status, sends reminders, verifies PayHere payments, runs bank-slip OCR and fraud checks. |
| Ticketing Agent                 | Issues dynamic monthly QR tickets and logs attendance at check-in.                                  |
| Marketing Agent                 | Captures and tags leads from ad click-to-WhatsApp entry points.                                     |
| Administrative Supervisor Agent | Detects escalation-worthy messages, tags urgency, and routes to the CRM inbox; flags trending FAQs. |
| Assignment Routing Agent        | Categorises and forwards submitted assignment photos to the correct paper-marker.                   |

## 10.2 Conceptual Data Flow

- Student/parent messages arrive via the WhatsApp Business API or Telegram Bot API into a channel-agnostic ingestion layer.
- An orchestration layer classifies intent and routes to the relevant agent(s); agents share a per-tenant knowledge base (Drive-synced resources) and a per-tenant student/CRM database.
- Payment events arrive either as PayHere webhook notifications or as bank-slip images; both converge on the Finance & Ledger Agent, which updates a single source-of-truth ledger per student.
- Anything the AI can't confidently resolve - academic, financial, or emotional/angry-parent - is written to the Escalation Inbox in the CRM with full context, rather than guessed at.
- All tenants are logically isolated; the Platform Super Admin layer sits above all tenants for billing, monitoring, and support.

# 11\. Data Model - Key Entities

| **Entity**            | **Description**                                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Tenant (Tutor/Agency) | A billing and data-isolation boundary; one independent tutor or agency.                                                       |
| Student               | A learner profile: name, school, district, class enrolments, language preference, consent status.                             |
| Parent/Guardian       | Linked to one or more students; receives reports and reminders.                                                               |
| Class / Subject       | A course offering with its fee schedule, resources, and roster.                                                               |
| Enrollment            | Links a student to a class, with status (active, paused, withdrawn).                                                          |
| Payment               | A financial transaction record: source (PayHere or bank slip), amount, status, verification method, linked receipt/QR ticket. |
| Attendance Record     | A timestamped check-in event linked to a student, class, and session date.                                                    |
| Assignment Submission | A photographed answer sheet, its grading result, and the assigned marker.                                                     |
| Escalation            | A conversation flagged for human review, with urgency, SLA timer, and resolution status.                                      |
| Lead                  | A prospective student captured pre-enrolment, with source and conversion status.                                              |
| Consent Record        | Evidence of PDPA-aligned opt-in/opt-out for a given data subject.                                                             |

# 12\. Third-Party Integrations and Technical Constraints

| **Integration**                      | **Key Constraints to Design Around**                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| WhatsApp Business API                | Per-delivered-message billing since mid-2025, split into Marketing / Utility / Authentication / Service categories with country-specific rates; free 24-hour service window opened by the user's message; free 72-hour window from Click-to-WhatsApp ad entry points; requires an approved Business Solution Provider and Meta template pre-approval. |
| Telegram Bot API                     | Free to use and generally more permissive on broadcast messaging, making it a valuable low-cost fallback channel, though it has lower penetration among Sri Lankan parents than WhatsApp.                                                                                                                                                             |
| PayHere                              | Sri Lanka's leading local payment gateway; supports Checkout, Recurring, Preapproval, Charging, Refund, and Subscription-Manager APIs; every webhook notification must be checksum-verified (md5sig) server-side before trusting the payment status; a public HTTPS notify URL is required (no localhost testing).                                    |
| OCR / Bank-slip verification         | No direct bank API access is assumed; verification relies on OCR plus heuristic/fraud checks (duplicate hash, amount/date match) rather than a guaranteed source-of-truth, so human review must remain in the loop for flagged cases.                                                                                                                 |
| Vision models (MCQ grading)          | Accuracy depends on photo quality (lighting, angle, handwriting); the system should validate image quality and prompt a re-upload rather than grading a poor image with false confidence.                                                                                                                                                             |
| LLM providers (conversational + RAG) | Must support large context windows for full syllabi/transcripts and ideally native Sinhala/Tamil handling; cost per token should be tracked per tenant (NFR-CO-03).                                                                                                                                                                                   |
| Google Drive                         | Assumed as the tutor's resource store for the RAG agent; requires OAuth access and a defined sync/refresh strategy so new uploads become searchable promptly.                                                                                                                                                                                         |

# 13\. Risk Register

| **Risk**                                                                                                                          | **Impact**                                                   | **Mitigation**                                                                                                                                                                           |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A tutor's WhatsApp number is restricted/banned by Meta for policy violations (e.g. excessive broadcast messaging).                | High - the tutor's entire operation could go dark.           | Cost-governance rules that bias toward free/service-window messaging (NFR-CO-01); Telegram failover (NFR-RE-04); template pre-approval discipline.                                       |
| LLM gives a confidently wrong academic answer.                                                                                    | High - erodes trust, could mislead a student before an exam. | Confidence thresholds with escalation to human (FR-AI-06); feedback-correction loop (FR-AI-07); grounding answers in the tutor's own vetted materials rather than open-domain knowledge. |
| Fraudulent or duplicated bank-transfer slip images.                                                                               | Medium-High - direct revenue leakage.                        | Duplicate-hash detection, amount/date matching, human review queue for flagged slips (FR-FI-05).                                                                                         |
| PDPA substantive provisions come into force with penalties before the platform is compliant.                                      | Medium - legal and reputational exposure.                    | Build consent capture, data-subject rights, and minimisation in from day one (Section 9.5) rather than retrofitting.                                                                     |
| WhatsApp per-message costs scale faster than tenant revenue as a tutor's student base grows.                                      | Medium - squeezes unit economics.                            | Per-tenant usage metering and budgets (FR-PL-03, NFR-CO-02); pricing model that passes through messaging costs transparently (Section 14).                                               |
| A single very large "star tutor" tenant creates a load spike (e.g. thousands of MCQ photos submitted right after one mass class). | Medium - could degrade response time platform-wide.          | Horizontal scaling and queuing for grading workloads (NFR-SC-03); immediate acknowledgement even if grading is asynchronous.                                                             |
| Over-reliance on a tutor's own Google Drive organisation for RAG quality.                                                         | Medium - poor answers if resources are messy or missing.     | Onboarding checklist and periodic "resource health" report suggesting gaps (e.g. missing notes for a topic students keep asking about).                                                  |
| Multiple children / family billing complexity causes reconciliation errors.                                                       | Low-Medium - parent confusion, support burden.               | Explicit family/sibling billing entity in the data model (FR-FI-07) rather than ad hoc workarounds.                                                                                      |

# 14\. Monetisation and SaaS Pricing Model (New)

Not part of the original draft, but necessary for an SRS meant to guide a fundable product: a suggested starting structure, to be validated with real tutors.

| **Tier**            | **Indicative Fit**                                 | **Structure**                                                                                                                                                                                       |
| ------------------- | -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Starter             | Independent tutor, up to ~150 students             | Flat monthly subscription covering core agents (Admissions, Resource, Academic Assistant, basic Finance); WhatsApp/Telegram messaging costs passed through at cost or bundled up to a fair-use cap. |
| Growth              | Growing tutor or small agency, ~150-1,000 students | Higher subscription tier unlocking the full CRM/Dashboard, escalation routing, MCQ grading, and attendance/ticketing; usage-based overage for messaging beyond the bundled allowance.               |
| Agency / Mass-Class | Top-tier institute, 1,000+ students                | Custom pricing with multi-staff roles, dedicated support, higher messaging allowances negotiated with the Business Solution Provider, and priority SLA.                                             |

Because Meta bills per delivered template message and rates vary sharply by category, the platform should pass through WhatsApp costs transparently (or bundle a conservative allowance) rather than absorbing an unpredictable variable cost inside a flat fee - this protects margin as tenants scale.

# 15\. Success Metrics / KPIs (New)

| **Metric**                                                    | **Why It Matters**                                                                                        |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| AI first-response resolution rate (no human needed)           | Directly measures the core value proposition: reducing tutor/admin workload.                              |
| Median response time to a student query                       | Reflects the "never overwhelmed, never asleep" promise.                                                   |
| Escalation SLA adherence rate                                 | Shows whether the human safety net is actually working, not just present.                                 |
| Payment reconciliation time (slip upload to confirmed status) | The core financial pain point Tutor AI is meant to eliminate.                                             |
| Fraud-flag precision/recall on bank slips                     | Balances not annoying honest payers against not missing fraud.                                            |
| Messaging cost per active student per month                   | Core unit-economics indicator given WhatsApp's per-message pricing.                                       |
| Tutor Net Promoter Score / renewal rate                       | Ultimate signal of whether tutors trust the platform with their business.                                 |
| Parent engagement rate with monthly progress reports          | Measures whether the platform is solving the "parental disconnect" problem, not just the tutor's problem. |

# 16\. Constraints and Assumptions

## 16.1 Constraints

- The system is bound by the messaging policies, template-approval process, and per-message rate limits of the WhatsApp Business API and Telegram Bot API.
- The system relies on external LLMs and vision models for Sinhala/Tamil voice-note processing and MCQ grading, inheriting their accuracy limits and cost structure.
- Bank-slip verification relies on OCR and heuristics rather than direct bank-system access, so it cannot be 100% automated with zero human oversight.
- PayHere (and card networks generally) require PCI-DSS-compliant handling; the platform must not touch raw card data directly.
- Sri Lanka's PDPA substantive provisions are still being operationalised as of mid-2026; exact enforcement timing is outside the product team's control (see Section 9.5).

## 16.2 Assumptions

- Students have access to smartphones with WhatsApp or Telegram installed.
- Tutors have their academic resources (PDFs, past papers) digitised and stored in an accessible format such as Google Drive for the RAG agent to retrieve.
- Tutors are willing to grant Tutor AI a Business Solution Provider connection to their WhatsApp Business number.
- Parents are reachable on the same or a linked WhatsApp/Telegram number and are willing to receive automated messages after consenting.

# 17\. Future Roadmap (Beyond v1)

Captured here so good ideas from brainstorming aren't lost, but explicitly deferred out of the v1 build to keep scope realistic.

- A lightweight LMS/web portal for students who want a browsable history of resources and scores.
- Native video hosting or deeper Zoom/Google Meet integration for recorded and live lectures.
- Automated essay/structured-answer grading (beyond MCQ), likely requiring a different, more nuanced model and a human-in-the-loop calibration process.
- Predictive at-risk-student flags combining attendance, payment lateness, and score trends, to help tutors intervene before a student drops out.
- Spaced-repetition or personalised revision scheduling driven by MCQ performance history.
- Gamification (leaderboards, streaks) for engagement, carefully scoped to avoid unhealthy competitive pressure among students.
- Federated multi-branch management for agencies operating across several physical locations.
- Student loan / instalment financing partnerships for fee payment.
- Expansion beyond Sri Lanka to other South Asian shadow-education markets with similar WhatsApp-first dynamics, which would also raise the question of full GDPR-equivalent compliance for any EU-adjacent user base.

# 18\. Glossary

| **Term**                               | **Definition**                                                                                                                                                                                        |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RAG (Retrieval-Augmented Generation)   | A technique the Resource Agent uses to fetch specific PDFs or video links from the tutor's own database based on a natural-language query, rather than relying purely on a model's general knowledge. |
| Shadow Education                       | Private tuition or supplementary academic instruction provided outside the formal school system for a fee.                                                                                            |
| OCR (Optical Character Recognition)    | Technology the Finance Agent uses to read and verify uploaded images of bank transfer slips.                                                                                                          |
| Singlish                               | Phonetic typing of Sinhala using the English alphabet (e.g. "Sir ada class thiyanawada?"), which the AI must interpret using NLP.                                                                     |
| Mass Class                             | Large-scale tuition lectures, particularly for A/L subjects, that may attract hundreds or thousands of students.                                                                                      |
| CRM (Customer Relationship Management) | In Tutor AI, the backend database and interface agency staff use to track student leads, profiles, payments, and academic progress.                                                                   |
| BSP (Business Solution Provider)       | A company approved by Meta to give businesses programmatic access to the WhatsApp Business API.                                                                                                       |
| Service Window                         | The free 24-hour period, opened whenever a user messages a business, during which replies are free of per-message charges.                                                                            |
| FEP (Free Entry Point)                 | A free 72-hour messaging window triggered when a user contacts a business via a Click-to-WhatsApp ad or Facebook Page CTA.                                                                            |
| PDPA                                   | Sri Lanka's Personal Data Protection Act, No. 9 of 2022 (as amended in 2025), which regulates the processing of personal data and establishes the Data Protection Authority of Sri Lanka.             |
| RBAC (Role-Based Access Control)       | A security model where dashboard permissions are assigned based on a staff member's role (e.g. paper marker vs. admin).                                                                               |
| SLA (Service-Level Agreement / Timer)  | A target response or resolution time attached to an escalation, used to prioritise the human queue.                                                                                                   |
| Tenant                                 | One tutor or agency's isolated account and dataset within the multi-tenant Tutor AI platform.                                                                                                         |

_- End of Document -_