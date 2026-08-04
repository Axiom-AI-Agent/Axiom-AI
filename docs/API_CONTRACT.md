# Dashboard API Contract (Phase 5)

REST endpoints for the Next.js staff dashboard. All routes require `tenant_id` as a query parameter unless noted.

**Design decisions:** [PHASE5_DECISIONS.md](PHASE5_DECISIONS.md) — escalation-only HITL, no separate payments queue.

**Base URL (local):** `http://localhost:8000`

**Auth (MVP):** Backend uses Supabase service role. Dashboard frontend should use Supabase Auth + RLS in production; these dev endpoints are unauthenticated for hackathon demos.

---

## Escalation inbox (unified HITL queue)

Payment receipts and talk-to-tutor requests both appear as **escalations** with different `reason_code` values.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/escalations?tenant_id=` | List inbox items |
| PATCH | `/dashboard/escalations/{id}/resolve?tenant_id=` | Approve payment or close tutor ticket |
| PATCH | `/dashboard/escalations/{id}/reject?tenant_id=` | Reject payment (no enrollment) |

Legacy alias: `/escalations` (same handlers).

### Query params (list)

| Param | Values |
|-------|--------|
| `status` | `open`, `assigned`, `resolved` |
| `reason_code` | `payment_receipt`, `talk_to_tutor` |

### Escalation object

```json
{
  "id": "esc-uuid",
  "tenant_id": "tenant-demo-physics",
  "student_id": "stu-physics-001",
  "student_name": "Amaya Perera",
  "student_phone": "94771234567",
  "enrollment_id": "enr-uuid",
  "reason_code": "payment_receipt",
  "status": "open",
  "media_url": "https://...",
  "student_message": "Here is my payment",
  "resolution": null,
  "reviewed_by": null,
  "reviewed_at": null,
  "created_at": "2026-08-04T12:00:00Z",
  "updated_at": "2026-08-04T12:00:00Z"
}
```

### Resolve (approve payment / close tutor)

```http
PATCH /dashboard/escalations/{id}/resolve?tenant_id=tenant-demo-physics&notify=true&reviewed_by=staff@demo.com
```

**Payment (`payment_receipt`):** activates pending enrollment, marks invoice paid, sends enrollment success WhatsApp.

**Tutor (`talk_to_tutor`):** marks resolved only (`resolution=closed`).

Response:

```json
{
  "ok": true,
  "escalation_id": "esc-uuid",
  "reason_code": "payment_receipt",
  "resolution": "approved",
  "enrollment_status": "active",
  "student_notified": true,
  "notification_message": "Great news, Amaya! ..."
}
```

### Reject payment

```http
PATCH /dashboard/escalations/{id}/reject?tenant_id=tenant-demo-physics&notify=true&reviewed_by=staff@demo.com
```

Only valid for `reason_code=payment_receipt`. Does **not** activate enrollment. Sends rejection WhatsApp.

---

## Overview stats

```http
GET /dashboard/overview?tenant_id=tenant-demo-physics
```

```json
{
  "tenant_id": "tenant-demo-physics",
  "open_escalations": 2,
  "open_payment_receipts": 1,
  "open_talk_to_tutor": 1,
  "pending_enrollments": 1,
  "students": 42,
  "classes": 3
}
```

---

## Chat logs & staff send

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/chat-logs?tenant_id=&phone=` | Conversation history (`st_turns`) |
| POST | `/dashboard/chat/send` | Staff → student WhatsApp |

### Chat logs

Same shape as `GET /chat/turns`:

```json
{
  "tenant_id": "tenant-demo-physics",
  "session_id": "tenant-demo-physics:94771234567",
  "turns": [
    {"id": "...", "role": "user", "content": "Hello", "created_at": "..."},
    {"id": "...", "role": "assistant", "content": "Hi!", "created_at": "..."}
  ]
}
```

### Staff send

```http
POST /dashboard/chat/send
Content-Type: application/json

{
  "tenant_id": "tenant-demo-physics",
  "phone": "94771234567",
  "message": "Your payment was approved — welcome to class!"
}
```

---

## Student → agent flows (for E2E testing)

Use `POST /chat` (see [DEV_CHAT.md](DEV_CHAT.md)):

1. **Payment receipt:** include `media_url` after pending enrollment exists
2. **Talk to tutor:** `"Can I speak to sir?"`

---

## MCP tools (agents)

| Tool | Purpose |
|------|---------|
| `create_escalation` | Open inbox item |
| `resolve_escalation` | Reason-aware resolve |
| `reject_payment_escalation` | Reject payment slip |

---

## Schema migration

Apply before first use:

```bash
make init-db
# or: psql "$SUPABASE_DB_URL" -f sql/02_phase5_escalations.sql
```

Adds to `escalations`: `media_url`, `student_message`, `resolution`, `reviewed_by`, `reviewed_at`.
