# Phase 5 — Design Decisions (As Implemented)

This document records the **intentional simplifications** taken during Phase 5 implementation. It supersedes the original Phase 5 sketch in the roadmap where those items differ.

**Related:** [API_CONTRACT.md](API_CONTRACT.md) · [DEV_CHAT.md](DEV_CHAT.md) · [Roadmap § Phase 5](Technical%20Docs/AI%20backend%20-%20Roadmap.md)

---

## Summary

Phase 5 delivers **human-in-the-loop (HITL)** via a **single escalation inbox**. Both payment receipts and talk-to-tutor requests create `escalations` rows; staff act from the dashboard. The bot **always completes its pipeline** — it never blocks waiting for a human.

---

## Core decision: escalation-only HITL

| Original roadmap idea | Decision | Rationale |
|----------------------|----------|-----------|
| Separate `payments` table + payment queue API | **One inbox:** `escalations` only | Less schema, one staff workflow, faster hackathon delivery |
| `bank_slip_uploads` storage | **No receipt table** — store `media_url` on escalation | Staff verify payment externally; link preserved for dashboard |
| `create_payment` MCP tool | **`create_escalation(reason_code=payment_receipt)`** | Same code path for all HITL items |
| `/dashboard/payments` approve/reject | **`/dashboard/escalations/{id}/resolve` and `/reject`** | Unified API surface |

---

## Flow 1 — Payment receipt

**Trigger:** Student sends payment slip image (`media_url` from Twilio or dev chat).

**Behaviour:**

1. Router forces `payment_check` when `media_url` is present.
2. **Payment Check agent** calls MCP `create_escalation` with `reason_code=payment_receipt`.
3. Student gets auto-ack: *"Thanks, team will verify…"*
4. Staff lists inbox → opens `media_url` → verifies offline.
5. **Approve:** `PATCH .../resolve` → activates pending enrollment, marks invoice paid, sends enrollment success WhatsApp.
6. **Reject:** `PATCH .../reject` → closes escalation only, sends rejection WhatsApp.

**Requires:** Pending enrollment exists (student completed admissions through consent). Otherwise agent returns a clear error.

**Not built:** OCR, auto-verification, PayHere, fraud detection (V2).

---

## Flow 2 — Talk to tutor

**Trigger:** Router detects escalation intent (e.g. "speak to sir", complaint, urgent).

**Behaviour:**

1. **Escalation agent** calls MCP `create_escalation` with `reason_code=talk_to_tutor`.
2. Student gets auto-ack: *"We've notified your tutor…"*
3. **Bot keeps chatting** on follow-up messages — no mute.
4. Staff resolves via dashboard when handled; optional `POST /dashboard/chat/send` for manual reply.

---

## Decisions explicitly skipped

| Item | Why skipped | V2 alternative |
|------|-------------|----------------|
| **`chat_sessions` + `human_mode`** | Added complexity; bot-mute not required for demo | `students.human_mode` column or session table |
| **Webhook on staff resolve** | Dashboard calls REST directly; simpler | Event bus / Supabase realtime |
| **Agent re-run on approve** | Template WhatsApp from resolve handler is enough | Full agent graph on resolve |
| **Infer mute from open escalation** | Bot should keep answering while student waits | Optional if double-reply becomes a problem |
| **Separate payment queue UI model** | Escalation inbox covers both flows | Dedicated payments module if volume grows |
| **`set_human_mode` MCP tool** | Not needed without human_mode storage | Phase 6+ if staff takeover is required |

---

## Reason codes

Defined in `src/domain/escalation_reasons.py`:

| Code | Meaning | On resolve | On reject |
|------|---------|------------|-----------|
| `payment_receipt` | Bank slip / payment image | Activate enrollment + notify | Notify rejection only |
| `talk_to_tutor` | Human help requested | Close ticket (`resolution=closed`) | N/A |
| `enrollment_payment_review` | Legacy alias | Treated as payment | Treated as payment |

Dedupe rule: one open escalation per `(tenant_id, student_id, reason_code)` (and `enrollment_id` for payments).

---

## Schema (Phase 5 migration)

File: `sql/02_phase5_escalations.sql`

Adds to `escalations`:

- `media_url` — receipt link for staff
- `student_message` — triggering message text
- `resolution` — `approved` \| `rejected` \| `closed`
- `reviewed_by`, `reviewed_at` — staff audit

No new `payments` or `chat_sessions` tables.

---

## Agent ownership

| Concern | Owner |
|---------|--------|
| Payment receipt + image | **Payment Check agent** (`payment_agent.py`) |
| Talk to tutor / complaint | **Escalation agent** (`escalation_agent.py`) |
| Onboarding slots, consent, class pick | **Admissions agent** (no longer handles media/receipts) |

All writes go through **`CrmTool`** → MCP `crm_server.py` (no duplicate DB logic in agent nodes).

---

## Dashboard API (implemented)

| Endpoint | Status |
|----------|--------|
| `GET /dashboard/escalations` | ✅ |
| `PATCH /dashboard/escalations/{id}/resolve` | ✅ |
| `PATCH /dashboard/escalations/{id}/reject` | ✅ |
| `GET /dashboard/overview` | ✅ |
| `GET /dashboard/chat/conversations` | ✅ Sidebar list |
| `GET /dashboard/chat/conversations/{phone}` | ✅ Thread + open escalations |
| `GET /dashboard/chat-logs` | ✅ Legacy alias |
| `POST /dashboard/chat/send` | ✅ Staff → student (persisted as `sender=staff`) |
| `GET/PATCH /dashboard/payments` | ❌ Skipped (use escalations) |
| `POST/PATCH /dashboard/classes` | ❌ Skipped (`GET /classes` exists) |

Full request/response shapes: [API_CONTRACT.md](API_CONTRACT.md).

---

## Acceptance criteria mapping

| Roadmap criterion | How we meet it |
|-------------------|----------------|
| Payment image → row visible in API | Escalation with `reason_code=payment_receipt` + `media_url` |
| Staff approve → Twilio to student | `PATCH .../resolve` |
| Staff reject → notify student | `PATCH .../reject` |
| Escalation in inbox | `GET /dashboard/escalations` |
| Staff send message | `POST /dashboard/chat/send` |
| Agents use MCP only | Payment + escalation agents → `create_escalation` |
| `API_CONTRACT.md` | ✅ |

---

## When to revisit (V2)

- High payment volume → dedicated payments module + OCR
- Staff need bot silence during takeover → `human_mode` flag
- Dashboard needs real-time updates → webhooks or Supabase Realtime
- Low-confidence RAG → auto-escalation (FR-AI-06)

---

*Last updated: Phase 5 completion — escalation-only HITL MVP.*
