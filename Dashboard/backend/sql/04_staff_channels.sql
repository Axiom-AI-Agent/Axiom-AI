-- Mirror of AI-backend/sql/08_staff_channels.sql for Dashboard create_all / manual apply.
-- Additive only.

CREATE TABLE IF NOT EXISTS staff_channels (
    id                  TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id           TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    staff_id            TEXT NOT NULL REFERENCES staff_users(id) ON DELETE CASCADE,
    channel             chat_channel NOT NULL,
    channel_address     TEXT NOT NULL,
    is_primary          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, channel, channel_address),
    UNIQUE (staff_id, channel)
);

CREATE INDEX IF NOT EXISTS idx_staff_channels_lookup
    ON staff_channels (tenant_id, channel, channel_address);

CREATE TABLE IF NOT EXISTS staff_link_codes (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    staff_id        TEXT NOT NULL REFERENCES staff_users(id) ON DELETE CASCADE,
    code            TEXT NOT NULL UNIQUE,
    expires_at      TIMESTAMPTZ NOT NULL,
    consumed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_staff_link_codes_lookup
    ON staff_link_codes (tenant_id, code);
