-- Phase 1: Timetable / Class Schedule
-- Adds recurring schedule templates and date-specific exceptions.
-- Safe to re-run.

-- ---------------------------------------------------------------------------
-- 1. New enums
-- ---------------------------------------------------------------------------

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'day_of_week') THEN
        CREATE TYPE day_of_week AS ENUM (
            'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday'
        );
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'schedule_status') THEN
        CREATE TYPE schedule_status AS ENUM (
            'active', 'cancelled'
        );
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'occurrence_status') THEN
        CREATE TYPE occurrence_status AS ENUM (
            'scheduled', 'cancelled', 'completed'
        );
    END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- 2. Add timezone to tenants
-- ---------------------------------------------------------------------------

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tenants' AND column_name = 'timezone'
    ) THEN
        ALTER TABLE tenants
            ADD COLUMN timezone TEXT NOT NULL DEFAULT 'Asia/Colombo';
    END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- 3. class_schedules — recurring weekly class templates
-- ---------------------------------------------------------------------------
-- Design decision: UNIQUE (tenant_id, class_id, day_of_week, start_time)
-- Allows multiple sessions per day (e.g. Physics at 9am AND 2pm on Tuesday).
-- Prevents duplicate sessions at the exact same time for the same class.

CREATE TABLE IF NOT EXISTS class_schedules (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    class_id        TEXT NOT NULL REFERENCES subject_classes(id) ON DELETE CASCADE,
    teacher_id      TEXT REFERENCES staff_users(id) ON DELETE SET NULL,
    day_of_week     day_of_week NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    room            TEXT,
    status          schedule_status NOT NULL DEFAULT 'active',
    effective_from  DATE NOT NULL DEFAULT CURRENT_DATE,
    effective_until DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (tenant_id, class_id, day_of_week, start_time)
);

CREATE INDEX IF NOT EXISTS idx_class_schedules_tenant
    ON class_schedules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_class_schedules_class
    ON class_schedules(class_id);
CREATE INDEX IF NOT EXISTS idx_class_schedules_teacher
    ON class_schedules(teacher_id);
CREATE INDEX IF NOT EXISTS idx_class_schedules_day
    ON class_schedules(tenant_id, day_of_week);
CREATE INDEX IF NOT EXISTS idx_class_schedules_query
    ON class_schedules(tenant_id, class_id, day_of_week, status);

-- ---------------------------------------------------------------------------
-- 4. class_schedule_exceptions — cancellations and reschedules
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS class_schedule_exceptions (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    schedule_id     TEXT NOT NULL REFERENCES class_schedules(id) ON DELETE CASCADE,
    exception_date  DATE NOT NULL,
    status          occurrence_status NOT NULL DEFAULT 'cancelled',
    new_start_time  TIME,
    new_end_time    TIME,
    new_room        TEXT,
    new_date        DATE,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (schedule_id, exception_date)
);

CREATE INDEX IF NOT EXISTS idx_schedule_exceptions_tenant
    ON class_schedule_exceptions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_schedule_exceptions_schedule
    ON class_schedule_exceptions(schedule_id);
CREATE INDEX IF NOT EXISTS idx_schedule_exceptions_date
    ON class_schedule_exceptions(tenant_id, exception_date);
