-- Migration 003: cost_events table
CREATE TABLE IF NOT EXISTS cost_events (
    event_id          UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id          UUID          NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    model             TEXT          NOT NULL,
    prompt_tokens     INT           NOT NULL DEFAULT 0,
    completion_tokens INT           NOT NULL DEFAULT 0,
    total_tokens      INT           NOT NULL DEFAULT 0,
    cost_usd          NUMERIC(12,8) NOT NULL DEFAULT 0,
    tool_name         TEXT,
    trace_id          UUID,
    team              TEXT,
    mcp_server_origin TEXT,
    timestamp         TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cost_events_agent_id  ON cost_events (agent_id);
CREATE INDEX IF NOT EXISTS idx_cost_events_timestamp ON cost_events (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_cost_events_team      ON cost_events (team);
CREATE INDEX IF NOT EXISTS idx_cost_events_trace_id  ON cost_events (trace_id);
CREATE INDEX IF NOT EXISTS idx_cost_events_model     ON cost_events (model);