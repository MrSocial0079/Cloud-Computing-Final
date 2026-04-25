package db

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

// DB wraps a pgxpool.Pool.
type DB struct {
	Pool *pgxpool.Pool
}

// NewPool creates a new connection pool for the given connString.
// Falls back to local docker-compose dev DSN if connString is empty.
func NewPool(ctx context.Context, connString string) (*pgxpool.Pool, error) {
	if connString == "" {
		connString = "postgres://invexsai:devpassword@localhost:5432/invexsai"
	}

	pool, err := pgxpool.New(ctx, connString)
	if err != nil {
		return nil, err
	}

	if err := pool.Ping(ctx); err != nil {
		return nil, err
	}

	return pool, nil
}

// HealthCheck verifies the pool can reach the database.
func HealthCheck(pool *pgxpool.Pool) error {
	return pool.Ping(context.Background())
}
