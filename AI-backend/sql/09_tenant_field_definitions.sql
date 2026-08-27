-- Per-tenant custom onboarding field definitions + student extra_fields.
-- Additive only — does not alter or drop existing student/tenant columns.
-- IDs are TEXT (matching tenants.id / students.id), not UUID.

CREATE TABLE IF NOT EXISTS tenant_field_definition (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    field_key       TEXT NOT NULL,
    label           TEXT NOT NULL,
    field_type      TEXT NOT NULL,
    options         JSONB,
    required        BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order      INT NOT NULL DEFAULT 0,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT tenant_field_definition_type_check
        CHECK (field_type IN ('text', 'number', 'select', 'boolean', 'date')),
    CONSTRAINT uq_tenant_field_definition_tenant_key
        UNIQUE (tenant_id, field_key)
);

CREATE INDEX IF NOT EXISTS idx_tenant_field_definition_tenant_sort
    ON tenant_field_definition (tenant_id, active, sort_order);

ALTER TABLE students
    ADD COLUMN IF NOT EXISTS extra_fields JSONB NOT NULL DEFAULT '{}'::jsonb;
