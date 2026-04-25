package services

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/invexsai/backend/internal/types"
	"github.com/jackc/pgx/v5/pgxpool"
)

type FleetService struct {
	db *pgxpool.Pool
}

func NewFleetService(db *pgxpool.Pool) *FleetService {
	return &FleetService{db: db}
}

// GetFleet returns a summary of all agents and their costs.
func (s *FleetService) GetFleet(ctx context.Context, filters types.FleetFilters) (*types.FleetResponse, error) {
	query := `
		SELECT
			a.agent_id, a.name, a.owner, a.framework, a.model,
			a.environment, a.status, a.tools, a.tags,
			a.registered_at, a.last_heartbeat_at,
			COALESCE(SUM(c.cost_usd), 0) as cost_usd_total,
			COALESCE(SUM(CASE WHEN c.timestamp > NOW() - INTERVAL '30 days' THEN c.cost_usd ELSE 0 END), 0) as cost_usd_30d,
			COUNT(c.event_id) as call_count_total
		FROM agents a
		LEFT JOIN cost_events c ON a.agent_id = c.agent_id
		WHERE 1=1`

	args := []interface{}{}
	argN := 1

	if filters.Environment != "" {
		query += fmt.Sprintf(" AND a.environment = $%d", argN)
		args = append(args, filters.Environment)
		argN++
	}
	if filters.Framework != "" {
		query += fmt.Sprintf(" AND a.framework = $%d", argN)
		args = append(args, filters.Framework)
		argN++
	}

	query += `
		GROUP BY a.agent_id, a.name, a.owner, a.framework, a.model,
		         a.environment, a.status, a.tools, a.tags,
		         a.registered_at, a.last_heartbeat_at`

	switch filters.Sort {
	case "cost_asc":
		query += " ORDER BY cost_usd_total ASC"
	case "name_asc":
		query += " ORDER BY a.name ASC"
	case "registered_desc":
		query += " ORDER BY a.registered_at DESC"
	default:
		query += " ORDER BY cost_usd_total DESC"
	}

	rows, err := s.db.Query(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	agents := []types.AgentSummary{}
	var totalCost float64

	for rows.Next() {
		var summary types.AgentSummary
		var tagsBytes []byte

		err := rows.Scan(
			&summary.AgentID, &summary.Name, &summary.Owner, &summary.Framework, &summary.Model,
			&summary.Environment, &summary.Status, &summary.Tools, &tagsBytes,
			&summary.RegisteredAt, &summary.LastHeartbeatAt,
			&summary.CostUSDTotal, &summary.CostUSD30D, &summary.CallCountTotal,
		)
		if err != nil {
			return nil, err
		}

		if err := json.Unmarshal(tagsBytes, &summary.Tags); err != nil {
			summary.Tags = map[string]string{}
		}
		if summary.Tools == nil {
			summary.Tools = []string{}
		}

		totalCost += summary.CostUSDTotal
		agents = append(agents, summary)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return &types.FleetResponse{
		TotalAgents:  len(agents),
		TotalCostUSD: totalCost,
		Agents:       agents,
	}, nil
}
