"""Add http_dev to chat_channel enum for dev /chat endpoint."""

ALTER TYPE chat_channel ADD VALUE IF NOT EXISTS 'http_dev';
