# Demo UI Plan — WhatsApp Mock + Full Agent Lifecycle

**Goal:** A self-contained **`demo-ui-org/`** folder that looks like a tuition centre (“Demo Physics Academy”) embedded a WhatsApp-style chatbot into their website. One **new mock student** can run the **full lifecycle** without Twilio or a separate dashboard repo.

**Reference (copy — do not invent):** BookMe AI `frontend/src/` — chat shell, bubbles, input, API client.  
**Backend:** Existing Axiom AI APIs only (`POST /chat`, dashboard routes). No new agent logic in the UI.

**Out of scope for v1:** Clerk auth, SSE streaming, BookMe landing/marketing pages, real Twilio.

---

## 1. Product concept

### Narrative (presenter script)

> “Demo Physics Academy added our AI assistant to their student portal. A new student opens chat, enrolls, pays, gets resources, and can escalate to a human — all on WhatsApp-style UI, powered by the same backend the production dashboard will use.”

### Two-pane demo layout (recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│  Demo Physics Academy — Student Portal          [Reset Demo]   │
├──────────────────────────────┬──────────────────────────────────┤
│  📱 WhatsApp Chat (student)  │  🛠 Staff Console (optional)     │
│                              │                                  │
│  [message bubbles]           │  Escalations inbox               │
│  [input + attach slip]       │  Approve / Reject payment        │
│                              │  Staff reply                     │
│                              │  Open escalations count          │
└──────────────────────────────┴──────────────────────────────────┘
```

- **Student pane:** WhatsApp look & feel → `POST /chat`
- **Staff pane:** Thin wrapper over existing dashboard APIs (no separate `Dashboard/backend` needed for demo)

Toggle **“Staff view”** for live demo moments (payment approve, tutor escalation).

---

## 2. Folder structure

```text
demo-ui-org/
├── README.md                    # Quick start + demo script
├── DEMO_SCRIPT.md               # Step-by-step presenter walkthrough
├── package.json                 # Optional workspace root (or per-app)
│
├── student-chat/                # Primary app — WhatsApp mock
│   ├── index.html
│   ├── vite.config.ts           # proxy /api → localhost:8000
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css            # WhatsApp palette overrides
│   │   ├── api/
│   │   │   └── client.ts        # ← adapt BookMe frontend/src/api/client.ts
│   │   ├── types.ts             # ← adapt BookMe types (Axiom ChatRequest/Response)
│   │   ├── hooks/
│   │   │   ├── useDemoSession.ts   # tenant + unique phone + localStorage
│   │   │   └── useChat.ts          # send + load turns (no SSE)
│   │   ├── components/
│   │   │   ├── WhatsAppShell.tsx   # header, wallpaper, phone frame
│   │   │   ├── MessageBubble.tsx   # ← adapt BookMe (green/white bubbles)
│   │   │   ├── ChatWindow.tsx      # ← adapt BookMe
│   │   │   ├── InputBox.tsx        # text + attach image (media_url)
│   │   │   ├── TypingIndicator.tsx
│   │   │   ├── DemoProgress.tsx    # lifecycle checklist UI
│   │   │   └── QuickActions.tsx    # chips: "Join class", "Explain velocity", etc.
│   │   └── pages/
│   │       └── ChatPage.tsx
│   └── public/
│       └── assets/
│           └── payment-slip-demo.jpg
│
├── staff-console/               # Secondary app OR tab in same SPA
│   └── src/
│       ├── api/dashboard.ts     # wraps API_CONTRACT endpoints
│       └── components/
│           ├── EscalationInbox.tsx
│           ├── EscalationDetail.tsx
│           └── StaffChatPanel.tsx
│
└── shared/
    ├── constants.ts             # TENANT_ID, API base, demo copy
    └── lifecycle.ts             # step definitions + detection helpers
```

**Naming:** `demo-ui-org` = “organisation that integrated the bot”. Alias in docs: `mock-ui` → same folder.

---

## 3. BookMe AI → Axiom file mapping

| BookMe AI source | Axiom demo action |
|------------------|-------------------|
| `frontend/src/components/MessageBubble.tsx` | Copy → restyle WhatsApp (green `#DCF8C6` user, white bot) |
| `frontend/src/components/ChatWindow.tsx` | Copy → scroll + message list |
| `frontend/src/components/InputBox.tsx` | Copy → add **attach file** → upload or preset `media_url` |
| `frontend/src/api/client.ts` | Adapt → `POST /chat`, `GET /chat/turns` (no SSE, no Clerk) |
| `frontend/src/types.ts` | Map to `ChatRequest`, `ChatResponse`, `ChatTurnRecord` |
| `frontend/src/index.css` + Tailwind | Copy scaffold; replace brand colours with WhatsApp |
| `frontend/vite.config.ts` | Proxy `/api` → `http://localhost:8000` |
| **Skip** | `useChatStream.ts`, `ChainOfThought`, `AuthGate`, `LandingPage`, Clerk |

**Dependencies (minimal):** React 18, Vite, Tailwind, `clsx`, `lucide-react`, optional `framer-motion`. No Clerk, no react-router unless staff tab needs routes.

---

## 4. API integration (student chat)

| UI action | Backend call |
|-----------|--------------|
| Send text | `POST /chat` `{ tenant_id, phone, message }` |
| Send payment slip | `POST /chat` + `media_url` (preset hosted image or blob→data URL) |
| Load history on refresh | `GET /chat/turns?tenant_id=&phone=` |
| Health indicator | `GET /health` |

### Mock student session (`useDemoSession`)

On **“Start new student demo”**:

1. Generate unique phone: `9477099{4-digit}` (same pattern as `smoke_st_memory.py`)
2. Persist in `localStorage`: `{ tenantId, phone, startedAt }`
3. Display as WhatsApp contact: “New Student (Demo)”

**Why unique phone:** Avoids stale enrollments / escalations from prior demos.

**Tenant:** Fixed `tenant-demo-physics` (Demo Physics Academy).

---

## 5. API integration (staff console)

Uses [API_CONTRACT.md](API_CONTRACT.md) — all calls include `X-Tenant-ID: tenant-demo-physics`.

| Staff action | Endpoint |
|--------------|----------|
| Inbox list | `GET /dashboard/escalations?status=open` |
| Filter payment | `?reason_code=payment_receipt` |
| Approve payment | `PATCH /dashboard/escalations/{id}/resolve` |
| Reject payment | `PATCH /dashboard/escalations/{id}/reject` |
| View thread | `GET /dashboard/chat/conversations/{phone}` |
| Staff reply | `POST /dashboard/chat/send` |
| Overview stats | `GET /dashboard/overview` |

Staff console polls inbox every **5s** during demo (simple `setInterval`, no WebSockets).

---

## 6. Full lifecycle demo script

| Step | Student says / does | Expected agent | Staff action | Progress tick |
|------|---------------------|----------------|--------------|---------------|
| **1** | “Hi, I want to join A/L Physics” | Admissions — ask name | — | Intent |
| **2** | Name, school, district | Slot filling | — | Profile |
| **3** | “A/L Physics” (class pick) | Lists / confirms class | — | Class |
| **4** | “YES” (consent) | Pending enrollment + payment instructions | — | Consent |
| **5** | Attach payment slip image | Payment agent ack + `payment_receipt` escalation | — | Payment sent |
| **6** | — | — | Staff **Approve** resolve | Enrolled |
| **7** | “Explain velocity from tutor notes” | Resource / RAG answer | — | Resource |
| **8** | “Can I speak to sir?” | Escalation ack + `talk_to_tutor` | Staff **Resolve** or reply | Escalation |
| **9** | (optional) “What's the weather?” | OOS polite redirect | — | Guardrail |

`DemoProgress.tsx` shows a **8-step checklist**; ticks update via keyword/heuristic detection on bot replies + staff actions (client-side only).

### Quick action chips (speed up live demo)

Pre-fill input:

- “I want to join A/L Physics”
- “Explain velocity from the notes”
- “Can I speak to sir?”
- Attach sample payment slip (one tap)

---

## 7. WhatsApp visual design

| Element | Spec |
|---------|------|
| Header | `#075E54`, tenant name + “online” |
| Wallpaper | Subtle WhatsApp doodle pattern (CSS or PNG) |
| User bubble | `#DCF8C6`, right-aligned, tail |
| Bot bubble | `#FFFFFF`, left-aligned, shadow |
| Timestamp | Small grey, under bubble |
| Input bar | Rounded, attach 📎 + send ➤ |
| Phone frame (optional) | CSS max-width 420px centred on desktop |

Bot avatar: tenant logo placeholder (“DPA” circle), not BookMe logo.

---

## 8. Implementation phases

### Phase A — Scaffold (~2h)

- [ ] Create `demo-ui-org/student-chat/` Vite + React + TS + Tailwind
- [ ] Copy/adapt BookMe `MessageBubble`, `ChatWindow`, `InputBox`
- [ ] Vite proxy to `:8000`
- [ ] `useDemoSession` + `useChat` hooks
- [ ] WhatsApp shell styling

**Done when:** Send message → see bot reply in green/white bubbles.

### Phase B — Student lifecycle (~2h)

- [ ] Quick action chips + demo script constants
- [ ] Image attach → `media_url` on `POST /chat`
- [ ] `GET /chat/turns` on mount (restore session)
- [ ] `DemoProgress` checklist component
- [ ] “Reset demo” → new phone, clear localStorage

**Done when:** Steps 1–5 and 7–9 work with backend running.

### Phase C — Staff console (~2h)

- [ ] Escalation inbox list + detail (payment `media_url` preview)
- [ ] Approve / Reject buttons
- [ ] Optional staff reply field
- [ ] Split view or tab toggle in `App.tsx`

**Done when:** Step 6 (approve payment) completes enrollment flow visibly.

### Phase D — Polish & docs (~1h)

- [ ] `demo-ui-org/README.md` + `DEMO_SCRIPT.md`
- [ ] Link from root `README.md`
- [ ] `make demo-ui` target (install + dev)
- [ ] Error states: backend down, 503, empty reply

**Total estimate:** ~7h (1 hackathon day)

---

## 9. Makefile / run instructions (planned)

```makefile
demo-ui-install:
	cd demo-ui-org/student-chat && npm install

demo-ui:
	cd demo-ui-org/student-chat && npm run dev
# Opens http://localhost:5173 — proxies API to :8000
```

**Prerequisites:** `make run` (API on 8000), `make init-db`, `OPENAI_API_KEY` set.

---

## 10. Technical decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| SSE streaming | **No** | Axiom `POST /chat` is request/response; simpler demo |
| Auth | **None** | Hackathon; tenant fixed in config |
| Image upload | **Preset URL** first | Avoid upload endpoint; use `public/assets/payment-slip-demo.jpg` as absolute URL or base64 |
| Monorepo vs single SPA | **Single SPA** with tabs | Faster: Student \| Staff in one Vite app |
| Separate `Dashboard/` backend | **Do not use** | Axiom AI backend already has dashboard routes |
| CORS | Vite dev proxy | Same as BookMe pattern |

---

## 11. Risks & mitigations

| Risk | Mitigation |
|------|------------|
| LLM slow on stage | Quick action chips; pre-warm API (`make run` loads MCP) |
| Duplicate enrollment | Unique phone per “Reset demo” |
| RAG empty | Run `make ingest-demo` before demo |
| Payment approve needs pending enrollment | Follow script order; show checklist |
| CORS in production build | nginx proxy or `VITE_API_URL` env |

---

## 12. Acceptance criteria

- [ ] New student can complete onboarding → payment → resource → escalation in UI only
- [ ] UI feels like WhatsApp (colours, bubbles, header)
- [ ] Staff can approve payment from same demo (split/tab view)
- [ ] “Reset demo” starts fresh student without DB manual cleanup
- [ ] Presenter can follow `DEMO_SCRIPT.md` in under 5 minutes
- [ ] No new backend endpoints required (UI consumes existing API only)

---

## 13. Future (post-hackathon)

- Embed widget `<script>` snippet for “org website integration” story
- Twilio Sandbox QR → same backend, real WhatsApp
- i18n Sinhala/Tamil quick actions
- Record/replay mode for offline demos

---

*Plan v1 — WhatsApp mock UI for Demo Physics Academy full agent lifecycle. Implement after approval.*
