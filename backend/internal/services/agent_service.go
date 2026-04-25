package services

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"time"

	"github.com/invexsai/backend/internal/types"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

var ErrAgentNotFound = errors.New("agent not found")

type AgentService struct {
	db *pgxpool.Pool
}

func NewAgentService(db *pgxpool.Pool) *AgentService {
	return &AgentService{db: db}
}

// Register creates a new agent or returns the existing one.
// Returns (response, existed, error) where existed=true means duplicate found (HTTP 200),
// existed=false means new insert (HTTP 201).
func (s *AgentService) Register(ctx context.Context, req types.RegisterRequest) (*types.RegisterResponse, bool, error) {
	name := strings.ToLower(strings.TrimSpace(req.Name))
	owner := strings.ToLower(strings.TrimSpace(req.Owner))

	var agentID string
	var registeredAt time.Time

	err := s.db.QueryRow(ctx,
		`SELECT agent_id, registered_at FROM agents WHERE name = $1 AND owner = $2`,
		name, owner,
	).Scan(&agentID, &registeredAt)

	if err == nil {
		return &types.RegisterResponse{
			AgentID:      agentID,
			Name:         name,
			RegisteredAt: registeredAt,
		}, true, nil
	}

	if !errors.Is(err, pgx.ErrNoRows) {
		return nil, false, err
	}

	// No existing agent — insert new one
	if req.Tools == nil {
		req.Tools = []string{}
	}
	if req.Tags == nil {
		req.Tags = map[string]string{}
	}

	err = s.db.QueryRow(ctx,
		`INSERT INTO agents (name, owner, framework, model, environment, tools, tags)
		 VALUES ($1, $2, $3, $4, $5, $6, $7)
		 RETURNING agent_id, registered_at`,
		name, owner, req.Framework, req.Model, req.Environment, req.Tools, req.Tags,
	).Scan(&agentID, &registeredAt)
	if err != nil {
		return nil, false, err
	}

	return &types.RegisterResponse{
		AgentID:      agentID,
		Name:         name,
		RegisteredAt: registeredAt,
	}, false, nil
}

// Heartbeat records a heartbeat for an agent and updates its status.
func (s *AgentService) Heartbeat(ctx context.Context, req types.HeartbeatRequest) (*types.HeartbeatResponse, error) {
	var exists bool
	err := s.db.QueryRow(ctx,
		`SELECT EXISTS(SELECT 1 FROM agents WHERE agent_id = $1)`,
		req.AgentID,
	).Scan(&exists)
	if err != nil {
		return nil, err
	}
	if !exists {
		return nil, ErrAgentNotFound
	}

	if req.Metadata == nil {
		req.Metadata = map[string]interface{}{}
	}
	metadataJSON, err := json.Marshal(req.Metadata)
	if err != nil {
		return nil, err
	}

	var recordedAt time.Time
	err = s.db.QueryRow(ctx,
		`INSERT INTO heartbeats (agent_id, status, latency_ms, metadata)
		 VALUES ($1, $2, $3, $4)
		 RETURNING recorded_at`,
		req.AgentID, req.Status, req.LatencyMs, metadataJSON,
	).Scan(&recordedAt)
	if err != nil {
		return nil, err
	}

	_, err = s.db.Exec(ctx,
		`UPDATE agents SET status = $1, last_heartbeat_at = $2 WHERE agent_id = $3`,
		req.Status, recordedAt, req.AgentID,
	)
	if err != nil {
		return nil, err
	}

	_, err = s.db.Exec(ctx,
		`UPDATE agents SET status = 'dead'
		 WHERE last_heartbeat_at < NOW() - INTERVAL '180 seconds'
		 AND status != 'dead'`,
	)
	if err != nil {
		return nil, err
	}

	return &types.HeartbeatResponse{
		RecordedAt:   recordedAt,
		NextExpected: recordedAt.Add(60 * time.Second),
	}, nil
}
