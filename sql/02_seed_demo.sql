-- Demo seed data — two tenants for hackathon + dashboard team testing

INSERT INTO tenants (id, name, slug, status, whatsapp_number, drive_folder_id)
VALUES
    ('tenant-demo-physics', 'Demo Physics Academy', 'demo-physics', 'active', 'whatsapp:+14155238886', 'drive-folder-physics-demo'),
    ('tenant-demo-chemistry', 'Demo Chemistry Institute', 'demo-chemistry', 'active', 'whatsapp:+14155238886', 'drive-folder-chemistry-demo')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    whatsapp_number = EXCLUDED.whatsapp_number,
    drive_folder_id = EXCLUDED.drive_folder_id,
    updated_at = NOW();

INSERT INTO parent_guardians (id, tenant_id, phone, name)
VALUES
    ('parent-physics-001', 'tenant-demo-physics', '94770001111', 'Nimal Perera'),
    ('parent-chemistry-001', 'tenant-demo-chemistry', '94770002222', 'Sunil Silva')
ON CONFLICT (id) DO NOTHING;

INSERT INTO subject_classes (id, tenant_id, subject, fee_amount, fee_cycle)
VALUES
    ('class-physics-al-2026', 'tenant-demo-physics', 'Physics', 5000.00, 'monthly'),
    ('class-chemistry-al-2026', 'tenant-demo-chemistry', 'Chemistry', 5500.00, 'monthly')
ON CONFLICT (id) DO NOTHING;

INSERT INTO students (id, tenant_id, parent_id, phone, name, district, language_pref)
VALUES
    ('stu-physics-001', 'tenant-demo-physics', 'parent-physics-001', '94771234567', 'Amaya Perera', 'Colombo', 'en'),
    ('stu-chemistry-001', 'tenant-demo-chemistry', 'parent-chemistry-001', '94779876543', 'Kavindu Silva', 'Colombo', 'en')
ON CONFLICT (id) DO NOTHING;

INSERT INTO enrollments (id, tenant_id, student_id, class_id, status)
VALUES
    ('enr-physics-001', 'tenant-demo-physics', 'stu-physics-001', 'class-physics-al-2026', 'active'),
    ('enr-chemistry-001', 'tenant-demo-chemistry', 'stu-chemistry-001', 'class-chemistry-al-2026', 'active')
ON CONFLICT (student_id, class_id) DO NOTHING;

INSERT INTO staff_users (id, tenant_id, role, name)
VALUES
    ('staff-physics-001', 'tenant-demo-physics', 'admin', 'Demo Physics Admin'),
    ('staff-chemistry-001', 'tenant-demo-chemistry', 'admin', 'Demo Chemistry Admin')
ON CONFLICT (id) DO NOTHING;

INSERT INTO invoices (id, tenant_id, student_id, period, amount_due, status)
VALUES
    ('inv-physics-2026-01', 'tenant-demo-physics', 'stu-physics-001', '2026-01', 5000.00, 'pending'),
    ('inv-chemistry-2026-01', 'tenant-demo-chemistry', 'stu-chemistry-001', '2026-01', 5500.00, 'pending')
ON CONFLICT (id) DO NOTHING;

INSERT INTO mem_procedures (id, tenant_id, name, description, steps, active)
VALUES
    (
        'proc-admissions-physics',
        'tenant-demo-physics',
        'admissions_onboarding',
        'Student onboarding workflow for new admissions',
        '[
            {"step": "greet", "prompt": "Welcome! Which class would you like to join?"},
            {"step": "name", "prompt": "What is your full name?"},
            {"step": "district", "prompt": "Which district are you from?"},
            {"step": "parent_phone", "prompt": "What is your parent/guardian WhatsApp number?"}
        ]'::jsonb,
        TRUE
    )
ON CONFLICT (tenant_id, name) DO NOTHING;
