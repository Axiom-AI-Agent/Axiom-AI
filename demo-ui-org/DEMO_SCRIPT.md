# Demo script — Student chat only (~5 min)

**Setup before presenting:** `make run`, `make init-db`, `make demo-ui`, optional `make ingest-demo`.

## Narrative

> “Demo Physics Academy embedded our AI assistant in their student portal. A new student opens WhatsApp-style chat, enrolls, pays, gets tutor notes, and can escalate — all powered by the same backend as production.”

Click **Reset demo** if you need a fresh student phone.

---

## Steps

| # | Action | Expected |
|---|--------|----------|
| 1 | Chip **Join A/L Physics** → send | Admissions agent asks for details |
| 2 | Chip **My details** → send | Slot filling (name, school) |
| 3 | Chip **Pick class** → send | Class confirmation |
| 4 | Chip **Consent YES** → send | Pending enrollment + payment instructions |
| 5 | Chip **Payment slip** (attach) | Ack + payment escalation created server-side |
| 6 | Chip **Explain velocity** → send | RAG answer from tutor notes (needs ingest) |
| 7 | Chip **Speak to sir** → send | Escalation ack (`talk_to_tutor`) |
| 8 | (optional) **OOS weather** | Polite out-of-scope redirect |

Lifecycle checklist ticks as you go (heuristic, client-side).

---

## Payment approval (outside this UI)

This UI is chat-only. To complete enrollment after step 5, approve in another tool:

```bash
# List open payment receipts
curl -s "http://localhost:8000/dashboard/escalations?tenant_id=tenant-demo-physics&reason_code=payment_receipt"

# Approve (replace {id})
curl -s -X PATCH "http://localhost:8000/dashboard/escalations/{id}/resolve?tenant_id=tenant-demo-physics&notify=true"
```

Or use the separate Dashboard app if running.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Red “API unreachable” | Start `make run`, check `:8000/health` |
| Empty RAG answer | Run `make ingest-demo` |
| Stale enrollment | **Reset demo** for new phone |
| Slow first reply | Pre-warm API; use quick-action chips |
