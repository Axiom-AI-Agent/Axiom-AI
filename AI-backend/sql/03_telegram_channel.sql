-- Telegram channel support: per-tenant bot credentials + student channel addresses.
-- Additive only — does not alter or drop existing columns.
-- Apply via scripts/init_supabase.py (lexical order after 01_schema / 02_*).

DO $$ BEGIN
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS bot_token TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

DO $$ BEGIN
    ALTER TABLE tenants ADD COLUMN IF NOT EXISTS telegram_bot_username TEXT;
EXCEPTION WHEN duplicate_column THEN NULL; END $$;

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
