-- Seed today's hardcoded onboarding extras (school, district) as field
-- definitions for every existing tenant. Core fields (name, class enrollment,
-- PDPA consent) stay out of this table.
-- Idempotent. Must run after 09_tenant_field_definitions.sql.

INSERT INTO tenant_field_definition (
    tenant_id,
    field_key,
    label,
    field_type,
    options,
    required,
    sort_order,
    active
)
SELECT
    t.id,
    'school',
    'School',
    'text',
    NULL,
    TRUE,
    0,
    TRUE
FROM tenants t
WHERE NOT EXISTS (
    SELECT 1
    FROM tenant_field_definition d
    WHERE d.tenant_id = t.id
      AND d.field_key = 'school'
);

INSERT INTO tenant_field_definition (
    tenant_id,
    field_key,
    label,
    field_type,
    options,
    required,
    sort_order,
    active
)
SELECT
    t.id,
    'district',
    'District',
    'text',
    NULL,
    TRUE,
    1,
    TRUE
FROM tenants t
WHERE NOT EXISTS (
    SELECT 1
    FROM tenant_field_definition d
    WHERE d.tenant_id = t.id
      AND d.field_key = 'district'
);
