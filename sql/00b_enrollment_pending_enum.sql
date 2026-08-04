-- Add enrollment_status 'pending' for payment-gated onboarding.
-- Must run in its own committed transaction before 01_schema.sql uses the value.

DO $$ BEGIN
    ALTER TYPE enrollment_status ADD VALUE IF NOT EXISTS 'pending';
EXCEPTION
    WHEN duplicate_object THEN NULL;
    WHEN undefined_object THEN NULL;
END $$;
