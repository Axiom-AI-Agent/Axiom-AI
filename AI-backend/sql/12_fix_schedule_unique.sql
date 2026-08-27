-- Fix: Replace UNIQUE constraint with partial unique index on active schedules only.
-- This allows re-creating a schedule after cancelling the previous one.

-- Drop the existing unique constraint
ALTER TABLE class_schedules
    DROP CONSTRAINT IF EXISTS class_schedules_tenant_id_class_id_day_of_week_start_time_key;

-- Create partial unique index (only applies to active schedules)
CREATE UNIQUE INDEX IF NOT EXISTS idx_class_schedules_active_unique
    ON class_schedules (tenant_id, class_id, day_of_week, start_time)
    WHERE status = 'active';
