# New Institution Setup — Complete Runbook

How to stand up a **new tuition institute (tenant)** on Axiom AI. This is not the demo-tenant path (`tenant-demo-physics`). Registration creates a real tenant with its own ID, staff, and locked onboarding fields; several production pieces are **not** created by the register form and must be done afterwards.

**Audience:** platform operator configuring a real institute.  
**Scope:** Dashboard + AI-backend + Supabase + Qdrant + Telegram + WhatsApp + Google Drive.  
**Last verified against:** `register_organization()`, `tenants` schema, channel resolvers, ingest pipeline, and dashboard settings.

---

## How an institution exists in this system

An institute **is** a row in `tenants`. Every other business table (`staff_users`, `students`, `subject_classes`, `enrollments`, `invoices`, `escalations`, `message_logs`, memory tables, `kb_documents`, schedules) is scoped by `tenant_id` and cascades on delete.

| Concept | Where it lives |
|---------|----------------|
| Identity | `tenants.id` — format `tenant-{slug}-{8 hex chars}` e.g. `tenant-apex-physics-a1b2c3d4` |
| URL-safe name | `tenants.slug` — unique, lowercase `a-z0-9` + hyphens |
| WhatsApp routing | `tenants.whatsapp_number` matched against Twilio **To** |
| Telegram routing | URL path `/webhooks/telegram/{tenant_id}` + `tenants.bot_token` |
| Drive resources | `tenants.drive_folder_id` (Google folder ID only, no query string) |
| RAG notes | Qdrant collection `axiom_kb_{tenant_id with hyphens→underscores}` |
| Student onboarding extras | `tenant_field_definition` rows; **locked** after registration |
| Payments master switch | `tenants.payments_enabled` (default `true`) |
| Class calendar | `tenants.timezone` (default `Asia/Colombo`) + `class_schedules` |

There is **no** self-serve UI for Telegram bot token, timezone, or Qdrant ingest. Those are operator steps.

---

## End-to-end order (do not skip)

```text
0. Platform once          Google SA, Twilio account, Langfuse, JWT, Qdrant
1. Schema                 make init-db + staff auth SQL
2. Register               /register  →  POST /auth/register
3. Post-register SQL      bot_token, telegram_bot_username, unique WhatsApp number
4. Classes + timetable    Dashboard Classes + Schedules
5. Channels               Telegram webhook; Twilio number uniqueness
6. Knowledge              Drive share + folder ID; Qdrant ingest
7. Staff ops              extra staff, Telegram staff-link
8. Verify                 chat, admissions, RAG, Drive, payments, dashboard
```

---

## Phase 0 — Platform prerequisites (once per environment)

These are **not** per-institute. Do them before the first real tenant.

### 0.1 Shared secrets

Both backends must share the same values from `AI-backend/.env` (Dashboard backend loads that file if `Dashboard/backend/.env` is absent).

| Variable | Required by | Notes |
|----------|-------------|--------|
| `SUPABASE_URL` | AI-backend | REST client |
| `SUPABASE_SERVICE_KEY` | AI-backend | Bypasses RLS; never put in the frontend |
| `SUPABASE_DB_URL` | Both | Postgres URL for `make init-db` and Dashboard SQLAlchemy |
| `JWT_SECRET_KEY` | Both | **Dashboard crashes at import if missing.** Same key used by AI-backend staff JWT (`dashboard agent` + Telegram staff link) |
| `JWT_ALGORITHM` | Both | Default `HS256` |
| `OPENAI_API_KEY` | AI-backend | Chat, router, embeddings |
| `QDRANT_URL` / `QDRANT_API_KEY` | AI-backend | Required for tutor-notes RAG |
| `LANGFUSE_*` | AI-backend | Optional; local prompt fallbacks work without keys |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | AI-backend | Platform-level, **not** per tenant |
| `TWILIO_WHATSAPP_FROM` | AI-backend | Sandbox default `whatsapp:+14155238886` |
| `TWILIO_WEBHOOK_URL` | AI-backend | Public URL used for signature validation |
| `MESSAGING_DRY_RUN` | AI-backend | `true` = log outbound, do not send |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | AI-backend | Absolute path to Drive SA JSON |
| `DRIVE_MOCK` | AI-backend | `false` for real Drive |
| `AGENT_USE_MCP` | AI-backend | `true` in production-like runs |
| `DEV_TENANT_ID` | AI-backend | **Local only.** Default `tenant-demo-physics`. WhatsApp messages that fail To-number match fall back here |

Frontend (`Dashboard/frontend/.env.local`):

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001
NEXT_PUBLIC_AI_API_URL=http://127.0.0.1:8000
NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8001
```

### 0.2 Google Drive (platform)

1. Google Cloud project → enable **Google Drive API**.
2. Create a **service account**, download JSON.
3. Put the JSON on the server and set `GOOGLE_SERVICE_ACCOUNT_JSON` + `DRIVE_MOCK=false`.
4. Keep the SA email — each institute must share their root folder with it as **Viewer**.

Detail: [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md).

### 0.3 Twilio (platform)

1. Twilio account → WhatsApp Sandbox (or a dedicated WhatsApp sender for production).
2. Set webhook to `https://<ai-backend-host>/webhooks/twilio`.
3. Sandbox: every student must send the **join code** once (e.g. `join happy-tiger`).
4. Production: **one WhatsApp sender number per tenant**. The resolver matches `tenants.whatsapp_number` against the message **To** field. Two tenants sharing one number cannot be distinguished (demo seed does this — do not copy that).

### 0.4 Langfuse (platform)

```bash
cd AI-backend
make seed-langfuse
```

Prompts are **not** per-tenant. Traces are tagged `tenant:{slug}` and `channel:{channel}`. Confirm the label in Langfuse UI matches `LANGFUSE_PROMPT_LABEL` (default `production`).

### 0.5 Three processes must be running for dashboard + chat

| Process | Command | Port |
|---------|---------|------|
| Dashboard backend | `cd Dashboard/backend && uvicorn app.main:app --reload --port 8001` | 8001 |
| AI backend | `cd AI-backend && make run` | 8000 |
| Dashboard frontend | `cd Dashboard/frontend && npm run dev` | 3000 |

---

## Phase 1 — Database schema

### 1.1 Apply AI-backend SQL (lexical order)

```bash
cd AI-backend
# Requires SUPABASE_DB_URL
make init-db
```

This runs **every** `AI-backend/sql/*.sql` file sorted by filename via `scripts/init_supabase.py`.

| File | Why a new tenant cares |
|------|------------------------|
| `00_drop_legacy.sql` | Destructive on v1 tables. Safe on a fresh project; **dangerous** if re-run against a populated DB that still has old names |
| `00b_enrollment_pending_enum.sql` | `pending` enrollment status (admissions confirm step) |
| `00c_chat_channel_http_dev.sql` | `http_dev` channel for `POST /chat` |
| `01_schema.sql` | Core schema including `tenants`, students, classes, memory, escalations |
| `02_phase5_escalations.sql` | Escalation review columns |
| `02_seed_demo.sql` | **Demo tenants only** — ignore for a real institute |
| `03_telegram_channel.sql` | `student_channels`, `bot_token`, `telegram_bot_username` |
| `04_telegram_pending.sql` | Phone capture before the student row exists |
| `05_kb_documents.sql` | Ingest registry |
| `06_human_mode_payments.sql` | `students.human_mode`, `tenants.payments_enabled` |
| `07_tutor_role.sql` | `staff_role.tutor` + extra fee cycles |
| `08_class_payments_enabled.sql` | Per-class payments flag |
| `08_staff_channels.sql` | Staff Telegram linking |
| `08_timetable.sql` | `tenants.timezone`, `class_schedules`, exceptions |
| `09_tenant_field_definitions.sql` | Custom onboarding fields + `students.extra_fields` |
| `10_seed_default_onboarding_fields.sql` | Seeds `school`/`district` for **already-existing** tenants only |
| `11_tenant_field_config_locked.sql` | Backfill lock flag where field defs already exist |

### 1.2 Apply Dashboard staff-auth columns (not in `init-db`)

`01_schema.sql` creates `staff_users` **without** `email` / `password_hash` / `is_active`. Registration **will fail** until this is applied:

```bash
psql "$SUPABASE_DB_URL" -f Dashboard/backend/sql/03_staff_auth.sql
```

This adds:

- `staff_users.email` + **global unique index** (`idx_staff_users_email`)
- `staff_users.password_hash`
- `staff_users.is_active` default `true`

`Dashboard/backend/sql/04_staff_channels.sql` mirrors `08_staff_channels.sql`. If `init-db` already ran, skip it.

**Do not rely on** Dashboard `Base.metadata.create_all` at startup. It creates missing tables from the ORM; it does **not** add columns to an existing `staff_users` table.

### 1.3 RLS

There are **no RLS policy files** in this repo. AI-backend uses the Supabase **service role** key (bypasses RLS). Dashboard uses custom JWT, not Supabase Auth. Tenant isolation is enforced in application queries (`tenant_id` on every table + JWT `tenant_id`).

---

## Phase 2 — Register the institution

This is the only step that creates the tenant row, admin, optional staff, and onboarding field definitions.

### 2.1 Collect from the institute (before opening `/register`)

| Ask them for | Used as | Required? |
|--------------|---------|-----------|
| Official name | `institution_name` → `tenants.name` + slug source | Yes |
| Admin name, email, password (≥ 8 chars, ≤ 72) | First `staff_users` row, role `admin` | Yes |
| Extra staff (up to 5): name, email, password, role | Additional `staff_users` | No |
| WhatsApp business / Twilio sender | `tenants.whatsapp_number` | Strongly recommended if WhatsApp is live |
| Google Drive **root folder ID** | `tenants.drive_folder_id` | If Drive resources are in scope |
| Extra student questions beyond name / phone / class / consent | `tenant_field_definition` | Decide now — **locked after submit** |
| Telegram bot display name + username | Later SQL (`bot_token`, `telegram_bot_username`) | If Telegram is live |
| Class catalogue (subject, grade, fee, cycle, schedule) | Created **after** register | Needed before students can enroll |
| Tutor notes (md/pdf/docx) | Qdrant ingest **after** a class exists | If RAG tutoring is in scope |

### 2.2 UI

Open `http://localhost:3000/register`  
(`Dashboard/frontend/src/app/register/page.tsx`)

The form posts `POST /auth/register` on the Dashboard backend (`:8001`).

### 2.3 What the API validates

`OrganizationRegisterRequest` in `Dashboard/backend/app/schemas/auth.py`:

| Field | Rules |
|-------|--------|
| `institution_name` | 2–200 chars, trimmed |
| `admin.name` | 2–100 |
| `admin.email` | Email, stored lowercase |
| `admin.password` | 8–72 (bcrypt limit) |
| `staff_members` | Max **5**; each same name/email/password rules; role ∈ `admin` \| `tutor` \| `marker` \| `viewer` |
| Emails | Unique within the payload **and** globally across `staff_users` (one email cannot belong to two institutes) |
| `onboarding_fields` | Max **15**; unique `field_key`; `select` needs ≥ 2 options |
| `field_key` | Starts with a letter; `[a-z0-9_]`; not reserved |

**Reserved field keys** (frontend + backend): `name`, `phone`, `class`, `course`, `consent`.  
Those are always collected by admissions. Do not add them as custom fields.

### 2.4 Onboarding fields — decide before submit

The register page pre-fills **School** (`school`) and **District** (`district`), both required text. You may:

- Keep them (recommended — they dual-write to `students.school` / `students.district` columns **and** `extra_fields`)
- Add more (text / number / select / boolean / date), up to 15
- Remove them all → students are only asked for **name**, then **class**, then **consent**

UI copy is explicit: *“This is locked after you create the institution.”*

`save_tenant_onboarding_fields(..., lock=True)` sets `tenants.field_config_locked = true`. After that, `PUT /tenant/onboarding-fields` returns **409**. There is no dashboard unlock UI.

`school` and `district` are **column-backed**. Other custom keys live only in `students.extra_fields` JSONB.

### 2.5 What registration actually writes

`register_organization()` (`Dashboard/backend/app/services/auth_service.py`):

1. Builds a unique slug: lowercase name, non-alphanumeric → `-`; if taken, `-2`, `-3`, …
2. Inserts tenant:
   - `id` = `tenant-{slug}-{uuid4.hex[:8]}`
   - `status` = `active`
   - optional `whatsapp_number`, `drive_folder_id`
3. Replaces field definitions and **locks** them.
4. Inserts admin (`role=admin`, `is_active=true`) + extra staff.
5. Commits. On any error, rolls back the whole transaction.

**Not written by registration:**

- `bot_token`, `telegram_bot_username`
- `timezone` (DB default `Asia/Colombo`)
- `payments_enabled` (DB default `true`)
- Any `subject_classes`, schedules, students, invoices
- `mem_procedures`
- Qdrant collection / KB files
- Telegram webhook

### 2.6 After success

The UI saves the JWT and redirects to `/dashboard/overview`.  
Copy the tenant id from Settings or `GET /tenant` — you need it for SQL, webhook, and ingest.

### 2.7 API-only alternative

```bash
curl -s -X POST http://127.0.0.1:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "institution_name": "Apex Physics",
    "whatsapp_number": "whatsapp:+9471XXXXXXX",
    "drive_folder_id": "1ABCxyzROOT_ID",
    "admin": {
      "name": "Nimal Perera",
      "email": "nimal@apex.lk",
      "password": "changeme-now"
    },
    "staff_members": [],
    "onboarding_fields": [
      {"field_key": "school", "label": "School", "field_type": "text", "required": true, "sort_order": 0},
      {"field_key": "district", "label": "District", "field_type": "text", "required": true, "sort_order": 1}
    ]
  }'
```

`201` + `access_token`. `409` if an email is already registered.

---

## Phase 3 — Post-register tenant row (SQL / operator)

Dashboard Settings can later edit name, slug, status, WhatsApp number, Drive folder ID. It **cannot** edit Telegram credentials or timezone (those columns are not on the Dashboard `Tenant` ORM / settings form).

### 3.1 Telegram bot (one bot per institute)

1. Telegram → [@BotFather](https://t.me/BotFather) → `/newbot`.
2. Display name (e.g. `Apex Physics Assistant`) and username ending in `bot`.
3. Save the **API token** like a password.

```sql
UPDATE tenants
SET bot_token = '<BOTFATHER_TOKEN>',
    telegram_bot_username = 'ApexPhysicsBot',  -- no @
    updated_at = NOW()
WHERE id = 'tenant-apex-physics-a1b2c3d4';
```

Tokens are **not** env vars. Lookup is `get_bot_token_for_tenant()` with a 5-minute in-process cache. After rotating a token, restart the AI backend (or the cache will serve the old value for up to 5 minutes). Suspended tenants (`status != active`) cannot send/receive Telegram.

### 3.2 WhatsApp number format

Store a value the resolver can match. It tries, in order:

1. Raw `To` from Twilio
2. Normalized `whatsapp:+{digits}`
3. Digits only

Recommended production value: `whatsapp:+94XXXXXXXXX`.

**Must be unique among active tenants.** Shared numbers fall through to `DEV_TENANT_ID` in development — that is how demo physics/chemistry both use the Twilio sandbox number. On a real deploy that fallback must not silently steal another institute’s traffic.

Settings → WhatsApp can be updated later (`PUT /tenant`).

### 3.3 Timezone (optional)

Default `Asia/Colombo`. To change:

```sql
UPDATE tenants SET timezone = 'Asia/Colombo', updated_at = NOW()
WHERE id = 'tenant-apex-physics-a1b2c3d4';
```

Used by the timetable, not by registration.

### 3.4 Payments master switch (optional)

Default `true`. `PUT /tenant` accepts `payments_enabled`, but the Settings form does **not** expose it. Per-class override exists in SQL (`subject_classes.payments_enabled`); identity ORs enrolled-class flags.

---

## Phase 4 — Classes and timetable

Students cannot finish admissions without at least one `subject_classes` row for the tenant. Ingest also **requires** a `class_id` (new tenants have no default in `TENANT_DEFAULT_CLASS`).

### 4.1 Create classes

Dashboard → **Classes**, or:

```http
POST /classes
Authorization: Bearer <staff JWT>
```

Body (`ClassCreate`): `subject` (required), `name`, `grade`, `fee_amount`, `fee_cycle`.

| `fee_cycle` | Values |
|-------------|--------|
| Allowed | `monthly`, `per_class`, `termly`, `one_time`, `annual` |

Class id is a UUID generated by the Dashboard backend. Copy it for ingest `--class-id`.

### 4.2 Timetable

Dashboard → **Schedules** (after classes exist).

- Recurring templates in `class_schedules`
- Unique `(tenant_id, class_id, day_of_week, start_time)` — two sessions on the same day are OK if start times differ
- Exceptions in `class_schedule_exceptions` (cancel / reschedule)
- Optional `teacher_id` → `staff_users`

### 4.3 Human mode / payments per class

- `PATCH /classes/{class_id}/human-mode` — when on, enrolled students skip auto-reply (`students.human_mode`)
- Per-class `payments_enabled` exists in SQL; the frontend currently calls a payments-enabled endpoint that the Dashboard backend may not implement — prefer SQL or tenant-level `payments_enabled` until that route exists

---

## Phase 5 — Messaging channels

### 5.1 Telegram webhook (required if Telegram is in use)

Public base URL of the **AI backend** (ngrok / production host), then:

```bash
cd AI-backend
PYTHONPATH=src python scripts/register_telegram_webhook.py \
  '<BOTFATHER_TOKEN>' \
  'tenant-apex-physics-a1b2c3d4' \
  'https://<ai-backend-public-host>'
```

This calls Telegram `setWebhook` with:

```text
https://<host>/webhooks/telegram/tenant-apex-physics-a1b2c3d4
```

Tenant is taken from the **URL path**, never from the message body. Confirm with `getWebhookInfo` printed by the script.

Inbound order in `telegram.py`:

1. Chat already in `staff_channels` → staff dashboard agent
2. Text matches `AXIOM-[A-F0-9]{8}` → consume staff link code
3. Else student handlers (contact share → onboarding / chat; photos → payment slip)

Students on Telegram **must share a phone number** (native contact button). Phone is the durable student id; `chat_id` is only the delivery address in `student_channels`.

### 5.2 WhatsApp / Twilio

1. Dedicated sender number mapped uniquely on `tenants.whatsapp_number`.
2. Twilio console webhook: `POST https://<host>/webhooks/twilio`.
3. Set `TWILIO_WEBHOOK_URL` to that exact public URL (signature check uses it).
4. `MESSAGING_DRY_RUN=false` only when you intend live sends.
5. Sandbox: students must join first.

`POST /chat` (HTTP) bypasses To-number lookup and takes `tenant_id` in the body — useful for smoke tests:

```bash
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-apex-physics-a1b2c3d4","phone":"94771234567","message":"Hello"}'
```

---

## Phase 6 — Knowledge (Drive + RAG)

These are **independent**. Drive = send file links. Qdrant = answer questions from tutor notes.

### 6.1 Google Drive (per institute)

Institute creates:

```text
{Institute Root}/          ← this folder’s ID goes in tenants.drive_folder_id
├── papers/
├── textbooks/
└── syllabus/
```

1. Share the **root** with the platform service-account email, role **Viewer**.
2. Folder ID = the path segment in `https://drive.google.com/drive/folders/<ID>` — **strip** `?usp=...`.
3. Set `drive_folder_id` at registration or later in Settings.
4. `.env`: `DRIVE_MOCK=false`, `GOOGLE_SERVICE_ACCOUNT_JSON=/absolute/path/key.json`.
5. Optional: `MCP_INCLUDE_DRIVE=true` to start the Drive MCP subprocess.

Smoke:

```bash
curl -s -X POST http://localhost:8000/tools/drive/search \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"tenant-apex-physics-a1b2c3d4","query":"paper","folder":"papers"}'
```

Empty results: SA not shared, wrong ID, files not in the three allowed subfolders, or still in mock mode.

### 6.2 Tutor notes → Qdrant (per institute)

1. Create at least one class (Phase 4) and copy its id.
2. Put files here (slug = `tenants.slug`):

```text
AI-backend/data/knowledge_base/{slug}/
  *.md | *.markdown | *.txt | *.pdf | *.docx
```

For a registered tenant, slug is derived from the name (e.g. Apex Physics → `apex-physics`). The ingest script maps only the two **demo** ids to slugs; for a real tenant it strips a `tenant-` prefix:

```text
tenant-apex-physics-a1b2c3d4  →  apex-physics-a1b2c3d4
```

That is **not** the same as `tenants.slug` (`apex-physics`). **Pass `--path` explicitly** for real tenants to avoid a silent empty/wrong folder:

```bash
cd AI-backend
mkdir -p data/knowledge_base/apex-physics
# copy notes into that folder

PYTHONPATH=src python scripts/ingest_tenant_notes.py \
  --tenant-id tenant-apex-physics-a1b2c3d4 \
  --class-id <subject_class_uuid> \
  --path data/knowledge_base/apex-physics
```

`--class-id` is **required** for non-demo tenants (`TENANT_DEFAULT_CLASS` only lists demo physics/chemistry).

Collection name: `axiom_kb_tenant_apex_physics_a1b2c3d4`  
(`qdrant_collection_for_tenant`: hyphens → underscores, prefix `axiom_kb` from `config/param.yaml`).

`make ingest-demo` only loads the two demo tenants — do not use it for a real institute.

RAG is **enrolled-only**: unenrolled phones get a “join a class” message, not notes.

---

## Phase 7 — Staff operations

### 7.1 More staff after registration

Dashboard → **Staff**, or `POST /staff` (JWT).  
Roles: `admin`, `tutor`, `marker`, `viewer`.  
Email unique **globally**. Inactive staff cannot log in (`is_active`).

### 7.2 Link staff Telegram (HITL / dashboard agent)

1. Confirm `telegram_bot_username` is set (Phase 3) so the UI can show `@bot`.
2. Settings → generate link code (`POST /auth/telegram/link-code`).
3. Code format `AXIOM-` + 8 hex chars, TTL **10 minutes**, previous unused codes for that staff are invalidated.
4. Staff opens the institute bot and pastes the code.
5. AI-backend writes `staff_channels` (`UNIQUE (staff_id, channel)` and `UNIQUE (tenant_id, channel, channel_address)`).
6. Later messages from that chat go to the **staff** agent, not student onboarding.

Unlink: Settings → unlink, or `DELETE /auth/telegram/link`.

### 7.3 JWT

Payload: `sub` (staff id), `tenant_id`, `email`, `role`, `exp`.  
Default expiry **480 minutes**. Dashboard `get_tenant_id()` always uses the token’s tenant — staff cannot switch institute.

---

## Phase 8 — Verify

Work through this against the **new** tenant id, not `tenant-demo-physics`.

| # | Check | How |
|---|--------|-----|
| 1 | Tenant row | `GET /tenant` as the new admin; id matches `tenant-{slug}-…`, status `active` |
| 2 | Login | `/login` with admin email |
| 3 | Classes | At least one class; students can be asked to pick it |
| 4 | HTTP chat | `POST /chat` with the new `tenant_id` + a new phone |
| 5 | Admissions | Name → custom fields → class list → YES consent → `enrollments.status=pending` |
| 6 | Onboarding lock | `GET /tenant/onboarding-fields` → `locked: true`; `PUT` → 409 |
| 7 | Telegram | Message the new bot; webhook path contains this tenant id; bot replies |
| 8 | Phone share | Telegram contact button creates/updates student + `student_channels` |
| 9 | WhatsApp | Message the **To** number stored on this tenant; must **not** land on demo tenant |
| 10 | RAG | After ingest + an **active** enrollment: “explain from lesson notes” cites Qdrant |
| 11 | Drive | “past paper / textbook / syllabus” returns links from this folder only |
| 12 | Payments | Slip photo → `payment_receipt` escalation in **this** tenant’s inbox |
| 13 | Escalation | “speak to tutor” → open escalation; staff reply from dashboard |
| 14 | Isolation | Tenant B staff JWT cannot read Tenant A students (403) |
| 15 | Langfuse | Trace tagged `tenant:{slug}` |
| 16 | Staff Telegram | `AXIOM-XXXXXXXX` links; subsequent chats are staff, not student |

Suspended tenant: set `status=suspended` in Settings. Telegram token lookup fails; WhatsApp resolver only matches `status=active`.

---

## What students experience (so you know setup is complete)

Admissions always collects, in order:

1. **Name**
2. Custom fields from `tenant_field_definition` (sort_order), unless you registered with zero extras
3. **Class** (must exist in `subject_classes`)
4. **Consent** (YES / bilingual confirm regex)
5. Pending enrollment; payment slip can follow if payments are enabled

Phone comes from WhatsApp `From` or Telegram shared contact — it is not a typed custom field.

Institute-info questions (“what classes do you offer?”, fees, staff names) read the same tenant/class/staff rows — they will be empty until Phase 4 / 7 are done.

---

## Optional: procedural memory

`register_organization()` does **not** seed `mem_procedures`. Admissions uses `tenant_field_definition`, not this table. Seed only if MCP `get_procedural` is required:

```sql
INSERT INTO mem_procedures (id, tenant_id, name, description, steps, active)
VALUES (
  gen_random_uuid()::text,
  'tenant-apex-physics-a1b2c3d4',
  'admissions_onboarding',
  'Student onboarding workflow',
  '[{"step":"name","prompt":"What is your full name?"}]'::jsonb,
  TRUE
)
ON CONFLICT (tenant_id, name) DO NOTHING;
```

---

## Gotchas (small details that break a new institute)

1. **`03_staff_auth.sql` is not in `make init-db`.** Registration needs `email` / `password_hash`.
2. **Onboarding fields lock on first save.** Wrong extras → no staff UI to fix; requires a manual DB unlock (`field_config_locked = false`) which is not a supported product flow.
3. **`bot_token` is not on the register form or Settings.** Telegram is dead until SQL + webhook.
4. **Dashboard `Tenant` ORM has no `bot_token` / `timezone`.** Do not expect the API to persist them.
5. **WhatsApp To-number must be unique.** Demo seed shares one sandbox number; `DEV_TENANT_ID` hides the bug locally.
6. **Ingest slug ≠ `tenants.slug` for registered ids.** Always pass `--path` and `--class-id`.
7. **`make ingest-demo` will not ingest the new tenant.**
8. **Drive folder ID must not include `?usp=sharing`.**
9. **Empty Drive mock** returns `files: []` — that is not a successful institute setup.
10. **Global staff email uniqueness** — a tutor cannot be invited to two institutes with the same email.
11. **Max 5 staff at register, 15 onboarding fields, password max 72.**
12. **JWT_SECRET_KEY must be identical** on Dashboard `:8001` and AI-backend `:8000` or staff Telegram / dashboard-agent auth fails.
13. **Token cache 5 minutes** after Telegram token rotation.
14. **Link code TTL 10 minutes**, uppercase hex only.
15. **`00_drop_legacy.sql` runs first on every `init-db`.** Do not casually re-init a live database.
16. **No RLS.** Isolation is application-level; the service key can read all tenants — keep it off the frontend.
17. **Enrolled-only RAG/Drive.** Creating classes is not enough; the test student needs an enrollment (admissions YES, or a manual `enrollments` row).
18. **Pending vs active enrollment.** Admissions confirm creates `pending`; payment E2E expects pending. Don’t mark `active` too early if you are testing slips.
19. **Human mode** on a student silences the bot — check it if “Telegram isn’t replying”.
20. **`field_definitions is []` vs `None`.** Empty list (locked at register with zero extras) does **not** fall back to school/district. Fallback `DEFAULT_FIELD_DEFINITIONS` only applies when definitions were never loaded (`None`).

---

## Copy-paste operator checklist

```text
[ ] Phase 0  .env complete (JWT, Supabase, OpenAI, Qdrant, Twilio, Drive SA)
[ ] Phase 0  make seed-langfuse (once)
[ ] Phase 1  make init-db
[ ] Phase 1  psql … 03_staff_auth.sql
[ ] Phase 2  Collect onboarding extras from the institute (locked after this)
[ ] Phase 2  Register at /register  →  copy tenant id
[ ] Phase 3  UPDATE tenants SET bot_token, telegram_bot_username
[ ] Phase 3  Confirm whatsapp_number unique + format whatsapp:+94…
[ ] Phase 4  Create classes (need class uuid for ingest)
[ ] Phase 4  Add weekly schedules if the institute uses a timetable
[ ] Phase 5  register_telegram_webhook.py
[ ] Phase 5  Twilio webhook + unique To number
[ ] Phase 6  Share Drive root with SA; set drive_folder_id; DRIVE_MOCK=false
[ ] Phase 6  ingest_tenant_notes.py --tenant-id --class-id --path
[ ] Phase 7  Extra staff; Telegram AXIOM- link
[ ] Phase 8  Run the verify table against THIS tenant id
```

---

## Related docs

- [SETUP.md](SETUP.md) — local stack, demo tenant
- [DATABASE.md](DATABASE.md) — schema reference
- [DRIVE_INTEGRATION.md](DRIVE_INTEGRATION.md) — Drive MCP
- [Axiom_AI_Telegram_Integration_Guide.md](Axiom_AI_Telegram_Integration_Guide.md) — one bot per tenant
- [Axiom_AI_Twilio_Integration_Guide.md](Axiom_AI_Twilio_Integration_Guide.md) — WhatsApp sandbox
- [DEV_CHAT.md](DEV_CHAT.md) — `POST /chat` without Twilio
- [FINALIZE_CHECKLIST.md](FINALIZE_CHECKLIST.md) — MVP sign-off (demo-oriented)
