package services

import (
	"context"
	"time"

	"github.com/invexsai/backend/internal/types"
	"github.com/jackc/pgx/v5/pgxpool"
)

type CostService struct {
	db *pgxpool.Pool
}

func NewCostService(db *pgxpool.Pool) *CostService {
	return &CostService{db: db}
}

// LogCost records a cost event for an agent invocation.
func (s *CostService) LogCost(ctx context.Context, req types.CostRequest) (*types.CostResponse, error) {
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

	var eventID string
	var timestamp time.Time
	err = s.db.QueryRow(ctx,
		`INSERT INTO cost_events (agent_id, model, prompt_tokens, completion_tokens, total_tokens, cost_usd, tool_name, trace_id, team, mcp_server_origin)
		 VALUES ($1, $2, $3, $4, $5, $6, $7, $8::uuid, $9, $10)
		 RETURNING event_id, timestamp`,
		req.AgentID, req.Model, req.PromptTokens, req.CompletionTokens, req.TotalTokens, req.CostUSD,
		req.ToolName, req.TraceID, req.Team, req.MCPServerOrigin,
	).Scan(&eventID, &timestamp)
	if err != nil {
		return nil, err
	}

	return &types.CostResponse{
		EventID:    eventID,
		RecordedAt: timestamp,
	}, nil
}
