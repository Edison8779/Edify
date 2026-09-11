-- ============================================================
-- Edify — PostgreSQL Initialization Script
-- Runs on first container startup only.
-- ============================================================

-- The database and user are already created by Docker's
-- POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB env vars.
-- This script is for any additional initialization.

-- Enable UUID extension (used for primary keys)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for future text search/similarity
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
