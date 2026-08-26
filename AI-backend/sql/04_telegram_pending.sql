-- Phone shared on Telegram before Admissions creates the student row.
-- Additive only — student_channels still requires a real students.id FK.

CREATE TABLE IF NOT EXISTS telegram_pending_contacts (
    tenant_id   TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    chat_id     TEXT NOT NULL,
    phone       TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tenant_id, chat_id)
);

CREATE INDEX IF NOT EXISTS idx_telegram_pending_phone
    ON telegram_pending_contacts (tenant_id, phone);
