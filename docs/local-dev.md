# Local development

This guide gets all three services running locally end-to-end so you can
develop against a realistic stack without connecting to AWS.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | 24+ | https://docs.docker.com/get-docker |
| Python | 3.11+ | https://python.org |
| Node.js | 20 LTS | https://nodejs.org |
| AWS CLI | 2.x | https://aws.amazon.com/cli |
| Terraform | 1.6+ | https://developer.hashicorp.com/terraform/install |

---

## First-time setup

### 1. Clone and configure

```bash
git clone https://github.com/your-org/sentinel-mas
cd sentinel-mas
cp .env.example .env
```

Open `.env` and fill in the required values. At minimum you need:

```
OPENAI_API_KEY=sk-...          # or Anthropic key if using Claude
DB_PASSWORD=localdev           # any value for local postgres
SQS_QUEUE_URL=                 # leave blank — docker-compose uses localstack
```

### 2. Start infrastructure services

```bash
docker compose up -d postgres localstack
```

Wait ~10 seconds for PostgreSQL to be ready:

```bash
docker compose logs postgres | grep "ready to accept connections"
```

### 3. Run database migrations

```bash
cd services/api
pip install -r requirements.txt
alembic upgrade head
```

### 4. Start all services

```bash
docker compose up
```

This starts `api`, `ui`, and `central` with hot-reload enabled. The first
build takes 2–3 minutes to install dependencies inside the containers.

### 5. Verify

| Service | URL |
|---------|-----|
| UI dashboard | http://localhost:3000 |
| API (docs) | http://localhost:8000/docs |
| API health | http://localhost:8000/health |
| LocalStack (SQS) | http://localhost:4566 |

---

## Day-to-day development

### Running a single service

If you only need to work on one service, you can run it directly rather than
through Docker:

```bash
# API service
cd services/api
uvicorn main:app --reload --port 8000

# UI service
cd services/ui
npm install
npm run dev

# Central agent
cd services/central
python -m sentinel_mas.main
```

The other services still need to run for integrations to work. Use
`docker compose up postgres localstack central` to keep dependencies alive
while you iterate on the API.

### Running tests

```bash
# All tests
make test

# Single service
cd services/api && pytest
cd services/central && pytest

# With coverage
pytest --cov=sentinel_mas --cov-report=term-missing
```

### Linting

```bash
make lint

# Or per service
cd services/api && ruff check . && mypy .
cd services/ui && npm run lint
```

---

## Working with the agent registry

The agent registry lives in `services/central/agents/crew_agents.py`. To add
or modify an agent locally:

1. Add or edit the `AgentRuntime` entry in `AGENT_REGISTRY`
2. Restart the central service: `docker compose restart central`
3. Send a test query via the API:

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me the last 10 security events in Hall A"}'
```

Watch the central service logs to see intent routing and tool calls:

```bash
docker compose logs -f central
```

---

## Working with Sentinel policy

The policy guardrail is configured in
`services/central/policy/sentinel_policy.py`. To test a policy change locally:

1. Modify the permitted tool list for an agent or adjust rate limit parameters
2. Restart the central service
3. Send a query that should trigger the policy (e.g. a cross-agent tool call)
4. Check logs for `PolicyRejection` events

Policy rejection events are logged at `WARN` level with the agent name,
requested tool, and rejection reason.

---

## Seeding test data

A seed script populates the local database with sample agents, tasks, and
audit log entries:

```bash
cd services/api
python scripts/seed.py
```

This creates:
- 3 agents (tracking, events, SOP) in `registered` state
- 20 sample security events across multiple zones
- 5 completed tasks with full audit trails

---

## Common issues

**Port already in use**

```bash
# Find what is using port 8000
lsof -i :8000
# Kill it
kill -9 PID
```

**Database connection refused**

Postgres takes ~10 seconds to start. Check it is ready before running
migrations:

```bash
docker compose ps postgres
```

If status is not `healthy`, wait and retry.

**Central agent not consuming from queue**

LocalStack SQS requires the queue to exist before the central agent starts.
If central started before localstack was ready:

```bash
docker compose restart central
```

**LLM API quota exceeded**

The central agent calls an LLM API for intent classification. If you hit
rate limits during development, add a `MOCK_LLM=true` flag to `.env` to
use a stub classifier that returns fixed intents.

---

## Connecting to dev AWS environment

To run services locally but against real AWS dev resources (RDS, SQS):

```bash
# Configure AWS CLI with dev credentials
aws configure --profile sentinel-dev

# Override .env to point at dev resources
AWS_PROFILE=sentinel-dev \
DB_HOST=sentinel-mas.XXXXXXXX.REGION.rds.amazonaws.com \
SQS_QUEUE_URL=https://sqs.REGION.amazonaws.com/ACCOUNT/sentinel-mas-tasks-dev \
uvicorn main:app --reload
```

Never point a local service at production resources.
