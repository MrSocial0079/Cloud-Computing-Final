package handlers

import (
	"errors"
	"net/http"
	"regexp"

	"github.com/gin-gonic/gin"
	"github.com/invexsai/backend/internal/services"
	"github.com/invexsai/backend/internal/types"
)

var uuidRE = regexp.MustCompile(`(?i)^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)

type CostHandler struct {
	svc *services.CostService
}

func NewCostHandler(svc *services.CostService) *CostHandler {
	return &CostHandler{svc: svc}
}

// LogCost handles POST /v1/agents/cost
func (h *CostHandler) LogCost(c *gin.Context) {
	var req types.CostRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		badField(c, "invalid JSON body", "")
		return
	}

	if req.AgentID == "" {
		badField(c, "agent_id is required", "agent_id")
		return
	}
	if !uuidRE.MatchString(req.AgentID) {
		badField(c, "agent_id must be a valid UUID", "agent_id")
		return
	}
	if req.Model == "" {
		badField(c, "model is required", "model")
		return
	}
	if req.PromptTokens < 0 {
		badField(c, "prompt_tokens must be >= 0", "prompt_tokens")
		return
	}
	if req.CompletionTokens < 0 {
		badField(c, "completion_tokens must be >= 0", "completion_tokens")
		return
	}
	if req.TotalTokens < 0 {
		badField(c, "total_tokens must be >= 0", "total_tokens")
		return
	}
	if req.CostUSD < 0 {
		badField(c, "cost_usd must be >= 0", "cost_usd")
		return
	}

	resp, err := h.svc.LogCost(c.Request.Context(), req)
	if err != nil {
		if errors.Is(err, services.ErrAgentNotFound) {
			c.JSON(http.StatusNotFound, types.ErrorResponse{Error: "agent not found", Code: 404})
			return
		}
		c.JSON(http.StatusInternalServerError, types.ErrorResponse{Error: "internal server error", Code: 500})
		return
	}

	c.JSON(http.StatusCreated, resp)
}
