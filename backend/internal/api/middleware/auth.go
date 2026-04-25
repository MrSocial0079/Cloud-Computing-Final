package middleware

import (
	"crypto/sha256"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/invexsai/backend/internal/types"
	"github.com/jackc/pgx/v5/pgxpool"
)

// APIKeyAuth returns a Gin middleware that validates the X-API-Key header
// against hashed keys stored in the api_keys table.
func APIKeyAuth(db *pgxpool.Pool) gin.HandlerFunc {
	return func(c *gin.Context) {
		apiKey := c.GetHeader("X-API-Key")
		if apiKey == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, types.ErrorResponse{
				Error: "missing API key",
				Code:  http.StatusUnauthorized,
			})
			return
		}

		hash := fmt.Sprintf("%x", sha256.Sum256([]byte(apiKey)))

		var keyID string
		err := db.QueryRow(c.Request.Context(),
			`SELECT key_id FROM api_keys WHERE key_hash = $1 AND revoked_at IS NULL`,
			hash,
		).Scan(&keyID)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusForbidden, types.ErrorResponse{
				Error: "invalid API key",
				Code:  http.StatusForbidden,
			})
			return
		}

		_, _ = db.Exec(c.Request.Context(),
			`UPDATE api_keys SET last_used_at = NOW() WHERE key_hash = $1`,
			hash,
		)

		c.Next()
	}
}
