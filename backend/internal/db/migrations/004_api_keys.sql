-- Migration 004: api_keys table
CREATE TABLE IF NOT EXISTS api_keys (
    key_id       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    key_hash     TEXT        NOT NULL UNIQUE,
    owner        TEXT        NOT NULL,
    description  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ,
    revoked_at   TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash   ON api_keys (key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_owner      ON api_keys (owner);
CREATE INDEX IF NOT EXISTS idx_api_keys_revoked_at ON api_keys (revoked_at) WHERE revoked_at IS NULL;