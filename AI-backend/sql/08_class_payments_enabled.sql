-- Per-class payment collection toggle (replaces org-wide enforcement)

ALTER TABLE subject_classes
    ADD COLUMN IF NOT EXISTS payments_enabled BOOLEAN NOT NULL DEFAULT TRUE;
