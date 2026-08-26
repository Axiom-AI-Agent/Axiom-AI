-- Knowledge-base document registry (ingest lifecycle + list/delete)
-- Apply after 01_schema.sql

CREATE TABLE IF NOT EXISTS kb_documents (
    id              TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    class_id        TEXT NOT NULL REFERENCES subject_classes(id) ON DELETE CASCADE,
    document_id     TEXT NOT NULL,
    filename        TEXT NOT NULL,
    title           TEXT,
    lesson          TEXT,
    source_type     TEXT NOT NULL,
    byte_size       BIGINT NOT NULL,
    page_count      INT,
    ocr_pages       INT NOT NULL DEFAULT 0,
    chunks_upserted INT,
    status          TEXT NOT NULL DEFAULT 'pending',
    error           TEXT,
    warnings        JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, document_id)
);

CREATE INDEX IF NOT EXISTS idx_kb_documents_tenant_class
    ON kb_documents (tenant_id, class_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_kb_documents_status
    ON kb_documents (tenant_id, status);
