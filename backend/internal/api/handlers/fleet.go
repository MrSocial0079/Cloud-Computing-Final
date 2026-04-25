package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/invexsai/backend/internal/services"
	"github.com/invexsai/backend/internal/types"
)

type FleetHandler struct {
	svc *services.FleetService
}

func NewFleetHandler(svc *services.FleetService) *FleetHandler {
	return &FleetHandler{svc: svc}
}

// GetFleet handles GET /v1/fleet
func (h *FleetHandler) GetFleet(c *gin.Context) {
	filters := types.FleetFilters{
		Environment: c.Query("environment"),
		Framework:   c.Query("framework"),
		Sort:        c.Query("sort"),
	}

	resp, err := h.svc.GetFleet(c.Request.Context(), filters)
	if err != nil {
		c.JSON(http.StatusInternalServerError, types.ErrorResponse{Error: "internal server error", Code: 500})
		return
	}

	c.JSON(http.StatusOK, resp)
}
