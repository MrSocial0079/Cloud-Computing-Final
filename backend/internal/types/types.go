package types

import "time"

type Agent struct {
	AgentID         string            `json:"agent_id"`
	Name            string            `json:"name"`
	Owner           string            `json:"owner"`
	Framework       string            `json:"framework"`
	Model           string            `json:"model"`
	Environment     string            `json:"environment"`
	Status          string            `json:"status"`
	Tools           []string          `json:"tools"`
	Tags            map[string]string `json:"tags"`
	RegisteredAt    time.Time         `json:"registered_at"`
	LastHeartbeatAt *time.Time        `json:"last_heartbeat_at,omitempty"`
}

type RegisterRequest struct {
	Name        string            `json:"name"`
	Owner       string            `json:"owner"`
	Framework   string            `json:"framework"`
	Model       string            `json:"model"`
	Environment string            `json:"environment"`
	Tools       []string          `json:"tools"`
	Tags        map[string]string `json:"tags"`
}

type HeartbeatRequest struct {
	AgentID   string                 `json:"agent_id"`
	Status    string                 `json:"status"`
	LatencyMs *int                   `json:"latency_ms"`
	Metadata  map[string]interface{} `json:"metadata"`
}

type CostEvent struct {
	EventID          string    `json:"event_id"`
	AgentID          string    `json:"agent_id"`
	Model            string    `json:"model"`
	PromptTokens     int       `json:"prompt_tokens"`
	CompletionTokens int       `json:"completion_tokens"`
	TotalTokens      int       `json:"total_tokens"`
	CostUSD          float64   `json:"cost_usd"`
	ToolName         *string   `json:"tool_name,omitempty"`
	TraceID          *string   `json:"trace_id,omitempty"`
	Team             *string   `json:"team,omitempty"`
	MCPServerOrigin  *string   `json:"mcp_server_origin,omitempty"`
	Timestamp        time.Time `json:"timestamp"`
}

type CostRequest struct {
	AgentID          string  `json:"agent_id"`
	Model            string  `json:"model"`
	PromptTokens     int     `json:"prompt_tokens"`
	CompletionTokens int     `json:"completion_tokens"`
	TotalTokens      int     `json:"total_tokens"`
	CostUSD          float64 `json:"cost_usd"`
	ToolName         *string `json:"tool_name"`
	TraceID          *string `json:"trace_id"`
	Team             *string `json:"team"`
	MCPServerOrigin  *string `json:"mcp_server_origin"`
}

type FleetResponse struct {
	TotalAgents  int            `json:"total_agents"`
	TotalCostUSD float64        `json:"total_cost_usd"`
	Agents       []AgentSummary `json:"agents"`
}

type AgentSummary struct {
	Agent
	CostUSDTotal   float64 `json:"cost_usd_total"`
	CostUSD30D     float64 `json:"cost_usd_30d"`
	CallCountTotal int     `json:"call_count_total"`
}

type RegisterResponse struct {
	AgentID      string    `json:"agent_id"`
	Name         string    `json:"name"`
	RegisteredAt time.Time `json:"registered_at"`
}

type HeartbeatResponse struct {
	RecordedAt   time.Time `json:"recorded_at"`
	NextExpected time.Time `json:"next_expected"`
}

type CostResponse struct {
	EventID    string    `json:"event_id"`
	RecordedAt time.Time `json:"recorded_at"`
}

type ErrorResponse struct {
	Error string `json:"error"`
	Field string `json:"field,omitempty"`
	Code  int    `json:"code"`
}

type FleetFilters struct {
	Environment string
	Framework   string
	Sort        string
}
