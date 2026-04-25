# InvexsAI — AI Agent Fleet Control Plane

A full-stack platform for registering, monitoring, and cost-tracking AI agent fleets in real time. Built as a cloud computing final project demonstrating microservice architecture, a Go REST API backend, a React dashboard, and a Python SDK with LangChain/AutoGen/CrewAI integrations.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (React)                    │
│          Vite · TypeScript · Tailwind CSS                │
│   Dashboard: fleet status, cost metrics, live badges     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / REST
┌──────────────────────▼──────────────────────────────────┐
│                  Backend (Go / Gin)                      │
│   /v1/agents/register   /v1/agents/heartbeat             │
│   /v1/agents/cost       /v1/fleet                        │
│   Auth: X-API-Key middleware                             │
└──────┬───────────────────────────────────────┬───────────┘
       │ pgx                                   │ (future)
┌──────▼───────┐                      ┌────────▼────────┐
│  PostgreSQL  │                      │     Redis       │
│  agents      │                      │  (cache / pub)  │
│  heartbeats  │                      └─────────────────┘
│  cost_events │
│  api_keys    │
└──────────────┘

┌─────────────────────────────────────────────────────────┐
│               Python SDK (invexsai)                      │
│   Async HTTP client + framework handlers                 │
│   LangChain · AutoGen · CrewAI integrations              │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | Go 1.23, Gin, pgx v5 |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Python SDK | Python 3.9+, httpx, langchain-core |
| Framework integrations | LangChain, AutoGen, CrewAI |
| Infrastructure | Docker Compose (local), Google Cloud Build (prod) |
| Auth | API key via `X-API-Key` header |

---

## Project Structure

```
.
├── backend/                  # Go REST API server
│   ├── cmd/server/main.go    # Entry point
│   ├── internal/
│   │   ├── api/              # Handlers, middleware, router
│   │   ├── db/               # Postgres pool + SQL migrations
│   │   ├── services/         # Business logic layer
│   │   └── types/            # Shared type definitions
│   └── Dockerfile
│
├── frontend/                 # React dashboard
│   └── src/
│       ├── App.tsx           # Main app + auth gate
│       ├── components/       # FleetTable, MetricCard, StatusBadge, etc.
│       ├── hooks/useFleet.ts # Fleet data fetching
│       └── api/fleet.ts      # API client
│
├── sdk/                      # Python SDK (pip install invexsai)
│   └── invexsai/
│       ├── client.py         # Async HTTP client
│       ├── heartbeat.py      # Heartbeat scheduler
│       ├── pricing.py        # Cost calculation
│       └── handlers/         # LangChain & AutoGen integrations
│
├── demo/                     # Example agent scripts
│   ├── demo_agent.py         # Standalone SDK demo
│   ├── demo_agent_autogen.py # AutoGen integration demo
│   └── demo_agent_crewai.py  # CrewAI integration demo
│
├── infra/
│   ├── docker-compose.yml    # Local dev environment
│   ├── cloudbuild.yaml       # GCP Cloud Build pipeline
│   └── scripts/              # GCP setup, migrations, API key helpers
│
└── .env.example              # Environment variable template
```

---

## Quick Start (Local with Docker)

### Prerequisites
- Docker & Docker Compose
- Go 1.23+ (for local backend dev)
- Node.js 18+ (for local frontend dev)
- Python 3.9+ (for SDK dev)

### 1. Clone & configure environment

```bash
git clone https://github.com/MrSocial0079/Cloud-Computing-Final.git
cd Cloud-Computing-Final
cp .env.example .env
# Edit .env and fill in your real values
```

### 2. Start the full stack

```bash
cd infra
docker-compose up --build
```

This starts:
- **Backend API** on `http://localhost:8080`
- **PostgreSQL** on `localhost:5432`
- **Redis** on `localhost:6379`

### 3. Run the frontend (dev mode)

```bash
cd frontend
npm install
npm run dev
# Dashboard available at http://localhost:5173
```

---

## API Reference

All `/v1/*` routes require the header:
```
X-API-Key: <your-api-key>
```

### Health Check
```
GET /health
```

### Register an Agent
```
POST /v1/agents/register
Content-Type: application/json

{
  "name": "my-agent",
  "framework": "langchain",
  "version": "1.0.0"
}
```

### Send Heartbeat
```
POST /v1/agents/heartbeat
Content-Type: application/json

{
  "agent_id": "uuid",
  "status": "running"
}
```

### Log Cost Event
```
POST /v1/agents/cost
Content-Type: application/json

{
  "agent_id": "uuid",
  "model": "gpt-4o",
  "input_tokens": 1000,
  "output_tokens": 500,
  "cost_usd": 0.0075
}
```

### Get Fleet Status
```
GET /v1/fleet
```

---

## Database Schema

```sql
-- agents: registered AI agents
CREATE TABLE agents (
  id          UUID PRIMARY KEY,
  name        TEXT NOT NULL,
  framework   TEXT,
  version     TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- heartbeats: agent liveness signals
CREATE TABLE heartbeats (
  id         BIGSERIAL PRIMARY KEY,
  agent_id   UUID REFERENCES agents(id),
  status     TEXT,
  ts         TIMESTAMPTZ DEFAULT NOW()
);

-- cost_events: per-LLM-call cost records
CREATE TABLE cost_events (
  id            BIGSERIAL PRIMARY KEY,
  agent_id      UUID REFERENCES agents(id),
  model         TEXT,
  input_tokens  INT,
  output_tokens INT,
  cost_usd      NUMERIC(10,6),
  ts            TIMESTAMPTZ DEFAULT NOW()
);

-- api_keys: auth tokens
CREATE TABLE api_keys (
  id         BIGSERIAL PRIMARY KEY,
  key_hash   TEXT UNIQUE NOT NULL,
  label      TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Python SDK Usage

### Installation

```bash
pip install invexsai
# Or with framework extras:
pip install "invexsai[langchain]"
pip install "invexsai[autogen]"
```

### Basic Usage

```python
import asyncio
from invexsai import InvexsaiClient

async def main():
    client = InvexsaiClient(
        base_url="http://localhost:8080",
        api_key="invexsai_dev_testkey123"
    )

    # Register your agent
    agent = await client.register_agent(
        name="my-langchain-agent",
        framework="langchain",
        version="1.0.0"
    )

    # Send heartbeats
    await client.send_heartbeat(agent_id=agent.id, status="running")

    # Log LLM costs
    await client.log_cost(
        agent_id=agent.id,
        model="gpt-4o",
        input_tokens=1200,
        output_tokens=400,
        cost_usd=0.009
    )

asyncio.run(main())
```

### LangChain Integration

```python
from invexsai.handlers.langchain import InvexsaiCallbackHandler

handler = InvexsaiCallbackHandler(
    client=client,
    agent_id=agent.id
)

# Pass to any LangChain chain/agent
chain = your_chain.with_config(callbacks=[handler])
```

### AutoGen Integration

```python
from invexsai.handlers.autogen import InvexsaiAutogenMonitor

monitor = InvexsaiAutogenMonitor(client=client, agent_id=agent.id)
# Attach to your AutoGen conversation group
```

---

## Running Demo Agents

```bash
cd demo

# Basic SDK demo
python demo_agent.py

# AutoGen demo
python demo_agent_autogen.py

# CrewAI demo
python demo_agent_crewai.py
```

---

## GCP Deployment

### Prerequisites
- Google Cloud project with billing enabled
- `gcloud` CLI authenticated
- Cloud SQL (PostgreSQL), Cloud Run, Container Registry enabled

### Steps

```bash
# 1. Set up GCP infrastructure
bash infra/scripts/setup_gcp.sh

# 2. Run database migrations
bash infra/scripts/run_migrations.sh

# 3. Create an API key
bash infra/scripts/create_api_key.sh

# 4. Deploy via Cloud Build
gcloud builds submit --config infra/cloudbuild.yaml
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Backend server port | `8080` |
| `DB_URL` | PostgreSQL connection string | `postgres://user:pass@host:5432/db` |
| `API_KEY` | Default API key for dev | `invexsai_dev_testkey123` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `OPENAI_API_KEY` | OpenAI key for demo agents | `sk-proj-...` |

Copy `.env.example` to `.env` and fill in real values. **Never commit `.env` to git.**

---

## Development

### Backend (Go)

```bash
cd backend
go mod tidy
go run ./cmd/server
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev       # dev server
npm run build     # production build
```

### SDK (Python)

```bash
cd sdk
pip install -e ".[dev,langchain,autogen]"
pytest tests/
```

---

## CI/CD

GitHub Actions workflow at `.github/workflows/ci.yml` runs on every push:
- Go build & vet
- Frontend type-check & build
- Python SDK tests

Cloud Build (`infra/cloudbuild.yaml`) handles production deployment to GCP Cloud Run.

---

## License

MIT — see LICENSE for details.
