-- Run this ONCE against an existing database that was created by the
-- first version of the API. A brand-new database doesn't need it — the
-- tables are created correctly on startup.
--
--   psql -U postgres -d mypos_db -f migrations/001_charisma_v2.sql

-- Payments now record when they were taken (used by the dashboard).
ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS paid_at TIMESTAMPTZ DEFAULT now();

-- Customer email is optional (many walk-in customers only give a phone number).
ALTER TABLE customers
    ALTER COLUMN email DROP NOT NULL;
