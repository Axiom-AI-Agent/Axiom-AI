-- Per-student AI mute + tenant payment submissions toggle

ALTER TABLE students
    ADD COLUMN IF NOT EXISTS human_mode BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE tenants
    ADD COLUMN IF NOT EXISTS payments_enabled BOOLEAN NOT NULL DEFAULT TRUE;
