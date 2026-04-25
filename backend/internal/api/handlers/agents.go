package handlers

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/invexsai/backend/internal/services"
	"github.com/invexsai/backend/internal/types"
)

type AgentHandler struct {
	svc *services.AgentService
}

func NewAgentHandler(svc *services.AgentService) *AgentHandler {
	return &AgentHandler{svc: svc}
}

var validFrameworks = map[string]bool{
	"langchain": true,
	"autogen":   true,
	"crewai":    true,
	"custom":    true,
}

var validEnvironments = map[string]bool{
	"development": true,
	"staging":     true,
	"production":  true,
}

var validStatuses = map[string]bool{
	"healthy":  true,
	"degraded": true,
	"error":    true,
}

func badField(c *gin.Context, msg, field string) {
	c.JSON(http.StatusBadRequest, types.ErrorResponse{Error: msg, Field: field, Code: 400})
}

// Register handles POST /v1/agents/register
func (h *AgentHandler) Register(c *gin.Context) {
	var req types.RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		badField(c, "invalid JSON body", "")
		return
	}

	if req.Name == "" {
		badField(c, "name is required", "name")
		return
	}
	if req.Owner == "" {
		badField(c, "owner is required", "owner")
		return
	}
	if req.Framework == "" {
		badField(c, "framework is required", "framework")
		return
	}
	if req.Model == "" {
		badField(c, "model is required", "model")
		return
	}
	if req.Environment == "" {
		badField(c, "environment is required", "environment")
		return
	}

	if !validFrameworks[req.Framework] {
		badField(c, "framework must be one of: langchain, autogen, crewai, custom", "framework")
		return
	}
	if !validEnvironments[req.Environment] {
		badField(c, "environment must be one of: development, staging, production", "environment")
		return
	}

	resp, existed, err := h.svc.Register(c.Request.Context(), req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, types.ErrorResponse{Error: "internal server error", Code: 500})
		return
	}

	if existed {
		c.JSON(http.StatusOK, resp)
	} else {
		c.JSON(http.StatusCreated, resp)
	}
}

// Heartbeat handles POST /v1/agents/heartbeat
func (h *AgentHandler) Heartbeat(c *gin.Context) {
	var req types.HeartbeatRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		badField(c, "invalid JSON body", "")
		return
	}

	if req.AgentID == "" {
		badField(c, "agent_id is required", "agent_id")
		return
	}
	if req.Status == "" {
		badField(c, "status is required", "status")
		return
	}
	if !validStatuses[req.Status] {
		badField(c, "status must be one of: healthy, degraded, error", "status")
		return
	}

	resp, err := h.svc.Heartbeat(c.Request.Context(), req)
	if err != nil {
		if errors.Is(err, services.ErrAgentNotFound) {
			c.JSON(http.StatusNotFound, types.ErrorResponse{Error: "agent not found", Code: 404})
			return
		}
		c.JSON(http.StatusInternalServerError, types.ErrorResponse{Error: "internal server error", Code: 500})
		return
	}

	c.JSON(http.StatusOK, resp)
}
