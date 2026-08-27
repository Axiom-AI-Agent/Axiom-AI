-- Dashboard mirror of AI-backend per-class payment collection toggle

ALTER TABLE subject_classes
    ADD COLUMN IF NOT EXISTS payments_enabled BOOLEAN NOT NULL DEFAULT TRUE;
