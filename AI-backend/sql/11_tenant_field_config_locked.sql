-- Lock onboarding field configuration after initial tenant setup.
-- Existing tenants that already have seeded field definitions skip the setup step.

ALTER TABLE tenants
    ADD COLUMN IF NOT EXISTS field_config_locked BOOLEAN NOT NULL DEFAULT false;

UPDATE tenants
SET field_config_locked = true
WHERE EXISTS (
    SELECT 1
    FROM tenant_field_definition d
    WHERE d.tenant_id = tenants.id
);
