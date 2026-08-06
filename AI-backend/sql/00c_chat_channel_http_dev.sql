-- Add http_dev to chat_channel enum for dev /chat endpoint.

DO $$ BEGIN
    ALTER TYPE chat_channel ADD VALUE IF NOT EXISTS 'http_dev';
EXCEPTION
    WHEN duplicate_object THEN NULL;
    WHEN undefined_object THEN NULL;
END $$;
