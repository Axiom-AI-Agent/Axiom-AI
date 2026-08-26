-- Axiom AI schema v2 — aligned with docs/Technical Docs/Tutor AI ER.png
-- Apply via scripts/init_supabase.py or Supabase SQL editor

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ---------------------------------------------------------------------------
-- Domain ENUM types
-- ---------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE tenant_status AS ENUM ('active', 'suspended');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE enrollment_status AS ENUM ('pending', 'active', 'paused', 'withdrawn');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE invoice_status AS ENUM ('pending', 'paid', 'overdue', 'disputed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE escalation_status AS ENUM ('open', 'assigned', 'resolved');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE message_role AS ENUM ('user', 'assistant', 'system');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE chat_channel AS ENUM ('twilio_whatsapp', 'telegram', 'http_dev');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE staff_role AS ENUM ('admin', 'marker', 'viewer');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE fee_cycle AS ENUM ('monthly', 'termly', 'annual');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Legacy enum kept for API compatibility (bank-slip review workflow)
DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('pending', 'approved', 'rejected');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------------------------------------------------------------------------
-- ORG_CONFIG → tenants (root tenant boundary + org settings)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tenants (
    id                  TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    slug                TEXT NOT NULL UNIQUE,
    status              tenant_status NOT NULL DEFAULT 'active',
    whatsapp_number         TEXT,
    drive_folder_id         TEXT,
    bot_token               TEXT,
    telegram_bot_username   TEXT,
    payments_enabled        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Backfill renamed columns when upgrading an existing tenants table
DO $$ BEGIN
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS whatsapp_number TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS drive_folder_id TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS bot_token TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS telegram_bot_username TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS payments_enabled BOOLEAN NOT NULL DEFAULT TRUE;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

-- ---------------------------------------------------------------------------
-- STAFF_USER + AUDIT_LOG
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS staff_users (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    role            staff_role NOT NULL DEFAULT 'admin',
    name            TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staff_users_tenant ON staff_users(tenant_id);

CREATE TABLE IF NOT EXISTS audit_logs (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    staff_id        TEXT NOT NULL REFERENCES staff_users(id) ON DELETE CASCADE,
    action          TEXT NOT NULL,
    target_type     TEXT NOT NULL,
    target_id       TEXT NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant ON audit_logs(tenant_id, timestamp DESC);

-- ---------------------------------------------------------------------------
-- PARENT_GUARDIAN + STUDENT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS parent_guardians (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    phone           TEXT NOT NULL,
    name            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, phone)
);

CREATE INDEX IF NOT EXISTS idx_parent_guardians_tenant_phone ON parent_guardians(tenant_id, phone);

CREATE TABLE IF NOT EXISTS students (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    parent_id       TEXT REFERENCES parent_guardians(id) ON DELETE SET NULL,
    name            TEXT,
    phone           TEXT NOT NULL,
    school          TEXT,
    district        TEXT,
    consent_at      TIMESTAMPTZ,
    language_pref   TEXT DEFAULT 'en',
    human_mode      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, phone)
);

DO $$ BEGIN
    ALTER TABLE students ADD COLUMN IF NOT EXISTS school TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE students ADD COLUMN IF NOT EXISTS consent_at TIMESTAMPTZ;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE students ADD COLUMN IF NOT EXISTS human_mode BOOLEAN NOT NULL DEFAULT FALSE;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

CREATE INDEX IF NOT EXISTS idx_students_tenant_phone ON students(tenant_id, phone);
CREATE INDEX IF NOT EXISTS idx_students_parent ON students(parent_id);

-- Channel delivery addresses (Telegram chat_id, WhatsApp number, etc.)
CREATE TABLE IF NOT EXISTS student_channels (
    id                  TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id           TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    student_id          TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    channel             chat_channel NOT NULL,
    channel_address     TEXT NOT NULL,
    is_primary          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, channel, channel_address),
    UNIQUE (student_id, channel)
);

CREATE INDEX IF NOT EXISTS idx_student_channels_lookup
    ON student_channels (tenant_id, channel, channel_address);

-- Phone shared on Telegram before Admissions creates the student row.
CREATE TABLE IF NOT EXISTS telegram_pending_contacts (
    tenant_id   TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    chat_id     TEXT NOT NULL,
    phone       TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tenant_id, chat_id)
);

CREATE INDEX IF NOT EXISTS idx_telegram_pending_phone
    ON telegram_pending_contacts (tenant_id, phone);

-- ---------------------------------------------------------------------------
-- SUBJECT_CLASS + ENROLLMENT
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subject_classes (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            TEXT,
    subject         TEXT NOT NULL,
    grade           TEXT,
    fee_amount      NUMERIC(12, 2) NOT NULL DEFAULT 0,
    fee_cycle       fee_cycle NOT NULL DEFAULT 'monthly',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DO $$ BEGIN
    ALTER TABLE subject_classes ADD COLUMN IF NOT EXISTS name TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE subject_classes ADD COLUMN IF NOT EXISTS grade TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

CREATE INDEX IF NOT EXISTS idx_subject_classes_tenant ON subject_classes(tenant_id);

DO $$ BEGIN
    ALTER TABLE students ADD COLUMN IF NOT EXISTS selected_class_id TEXT REFERENCES subject_classes(id) ON DELETE SET NULL;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS enrollments (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    student_id      TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    class_id        TEXT NOT NULL REFERENCES subject_classes(id) ON DELETE CASCADE,
    status          enrollment_status NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, class_id)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_tenant ON enrollments(tenant_id);

DO $$ BEGIN
    ALTER TABLE enrollments ALTER COLUMN status SET DEFAULT 'pending';
EXCEPTION WHEN undefined_table THEN NULL; END $$;

-- ---------------------------------------------------------------------------
-- INVOICE + BANK_SLIP_UPLOAD
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS invoices (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    student_id      TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    period          TEXT NOT NULL,
    amount_due      NUMERIC(12, 2) NOT NULL,
    status          invoice_status NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_tenant_status ON invoices(tenant_id, status);

CREATE TABLE IF NOT EXISTS bank_slip_uploads (
    id                  TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id           TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    invoice_id          TEXT NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    image_ref           TEXT NOT NULL,
    confidence_score    REAL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bank_slip_uploads_invoice ON bank_slip_uploads(invoice_id);

-- ---------------------------------------------------------------------------
-- MESSAGE_LOG + ESCALATION
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS message_logs (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    student_id      TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    channel         chat_channel NOT NULL DEFAULT 'twilio_whatsapp',
    intent          TEXT,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_message_logs_tenant_student ON message_logs(tenant_id, student_id, timestamp DESC);

CREATE TABLE IF NOT EXISTS escalations (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    student_id      TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    enrollment_id   TEXT REFERENCES enrollments(id) ON DELETE SET NULL,
    reason_code     TEXT NOT NULL,
    status          escalation_status NOT NULL DEFAULT 'open',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DO $$ BEGIN
    ALTER TABLE escalations ADD COLUMN IF NOT EXISTS enrollment_id TEXT REFERENCES enrollments(id) ON DELETE SET NULL;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

CREATE INDEX IF NOT EXISTS idx_escalations_tenant_status ON escalations(tenant_id, status);

-- ---------------------------------------------------------------------------
-- Memory tables (pgvector)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mem_procedures (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    description     TEXT,
    steps           JSONB NOT NULL DEFAULT '[]'::jsonb,
    embedding       vector(1536),
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, name)
);

CREATE TABLE IF NOT EXISTS mem_facts (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    text            TEXT NOT NULL,
    embedding       vector(1536),
    score           REAL NOT NULL DEFAULT 0,
    tags            JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mem_facts_tenant_user ON mem_facts(tenant_id, user_id);

CREATE TABLE IF NOT EXISTS mem_episodes (
    id                  TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id           TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id             TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_id          TEXT NOT NULL,
    summary             TEXT,
    summary_embedding   vector(1536),
    turns               JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mem_episodes_session ON mem_episodes(tenant_id, session_id);

CREATE TABLE IF NOT EXISTS st_turns (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    session_id      TEXT NOT NULL,
    role            message_role NOT NULL,
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_st_turns_session ON st_turns(tenant_id, session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_st_turns_user ON st_turns(tenant_id, user_id, created_at DESC);
