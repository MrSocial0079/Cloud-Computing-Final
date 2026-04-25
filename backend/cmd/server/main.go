package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/invexsai/backend/internal/api"
	"github.com/invexsai/backend/internal/db"
	"github.com/joho/godotenv"
)

func main() {
	// Load .env for local dev; ignore error if file not present
	_ = godotenv.Load()

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	dbURL := os.Getenv("DB_URL")

	pool, err := db.NewPool(context.Background(), dbURL)
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}
	if pool != nil {
		defer pool.Close()
	}

	router := api.NewRouter(pool)

	fmt.Printf("INVEXSAI backend running on :%s\n", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
