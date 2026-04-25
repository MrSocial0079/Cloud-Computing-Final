package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/invexsai/backend/internal/api/handlers"
	"github.com/invexsai/backend/internal/api/middleware"
	"github.com/invexsai/backend/internal/services"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Router struct {
	engine       *gin.Engine
	db           *pgxpool.Pool
	agentHandler *handlers.AgentHandler
	costHandler  *handlers.CostHandler
	fleetHandler *handlers.FleetHandler
}

func NewRouter(db *pgxpool.Pool) *Router {
	agentSvc := services.NewAgentService(db)
	costSvc := services.NewCostService(db)
	fleetSvc := services.NewFleetService(db)

	agentHandler := handlers.NewAgentHandler(agentSvc)
	costHandler := handlers.NewCostHandler(costSvc)
	fleetHandler := handlers.NewFleetHandler(fleetSvc)

	r := &Router{
		engine:       gin.Default(),
		db:           db,
		agentHandler: agentHandler,
		costHandler:  costHandler,
		fleetHandler: fleetHandler,
	}

	r.registerRoutes()
	return r
}

func (r *Router) registerRoutes() {
	r.engine.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	v1 := r.engine.Group("/v1")
	v1.Use(middleware.APIKeyAuth(r.db))
	{
		agents := v1.Group("/agents")
		{
			agents.POST("/register", r.agentHandler.Register)
			agents.POST("/heartbeat", r.agentHandler.Heartbeat)
			agents.POST("/cost", r.costHandler.LogCost)
		}

		v1.GET("/fleet", r.fleetHandler.GetFleet)
	}
}

func (r *Router) Run(addr string) error {
	return r.engine.Run(addr)
}
