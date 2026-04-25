-- Migration 002: heartbeats table
CREATE TABLE IF NOT EXISTS heartbeats (
    heartbeat_id UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id     UUID        NOT NULL REFERENCES agents (agent_id) ON DELETE CASCADE,
    status       TEXT        NOT NULL,
    latency_ms   INT,
    metadata     JSONB       NOT NULL DEFAULT '{}',
    recorded_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_heartbeats_agent_id    ON heartbeats (agent_id);
CREATE INDEX IF NOT EXISTS idx_heartbeats_recorded_at ON heartbeats (recorded_at DESC);
