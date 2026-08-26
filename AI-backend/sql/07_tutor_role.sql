-- Tutor staff role + fee cycle values used by Dashboard class schemas.
-- Safe to re-run.

ALTER TYPE staff_role
    ADD VALUE IF NOT EXISTS 'tutor';

ALTER TYPE fee_cycle
    ADD VALUE IF NOT EXISTS 'per_class';

ALTER TYPE fee_cycle
    ADD VALUE IF NOT EXISTS 'one_time';
