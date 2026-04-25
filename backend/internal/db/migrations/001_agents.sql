-- Migration 001: agents table
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS agents (
    agent_id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name              TEXT        NOT NULL,
    owner             TEXT        NOT NULL,
    framework         TEXT        NOT NULL CHECK (framework IN ('langchain','autogen','crewai','custom')),
    model             TEXT        NOT NULL,
    environment       TEXT        NOT NULL DEFAULT 'development' CHECK (environment IN ('development','staging','production')),
    status            TEXT        NOT NULL DEFAULT 'healthy',
    tools             TEXT[]      NOT NULL DEFAULT '{}',
    tags              JSONB       NOT NULL DEFAULT '{}',
    registered_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_heartbeat_at TIMESTAMPTZ,
    CONSTRAINT uq_agents_name_owner UNIQUE (name, owner)
);

CREATE INDEX IF NOT EXISTS idx_agents_owner       ON agents (owner);
CREATE INDEX IF NOT EXISTS idx_agents_environment ON agents (environment);
CREATE INDEX IF NOT EXISTS idx_agents_framework   ON agents (framework);
CREATE INDEX IF NOT EXISTS idx_agents_status      ON agents (status);
CREATE INDEX IF NOT EXISTS idx_agents_tags        ON agents USING GIN (tags);