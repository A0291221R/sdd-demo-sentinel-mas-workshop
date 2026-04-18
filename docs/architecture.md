# Architecture

## Overview

Sentinel MAS is a multi-agent system for security monitoring and automated
remediation. It coordinates specialised agents through a central orchestrator,
routes natural language queries to the correct domain agent, and enforces
tool access via a policy guardrail layer.

The system is deployed on AWS ECS Fargate with blue/green deployments managed
by CodeDeploy. All infrastructure is defined in Terraform.

---

## System components

### Services

| Service | Language | Purpose |
|---------|----------|---------|
| `central` | Python 3.11 | Orchestrator — routes intents, manages agent lifecycle |
| `api` | Python 3.11 / FastAPI | REST interface for external consumers and the UI |
| `ui` | TypeScript / React 18 | Operator dashboard |

### Infrastructure

| Component | Service | Notes |
|-----------|---------|-------|
| Compute | ECS Fargate | Serverless; no node management |
| Load balancer | ALB | Routes `/api/*` to API service, `/*` to UI |
| Database | RDS PostgreSQL 15 | Agent state (JSONB), audit log, task queue |
| Message queue | SQS (standard) | Decouples event sources from the orchestrator |
| Deployments | CodeDeploy | Blue/green with 10-minute bake period |
| Secrets | Secrets Manager | Injected into ECS task environment at launch |
| Registry | ECR | Container images; co-located with ECS |
| IaC | Terraform 1.6+ | Modular; dev and prod workspaces |

---

## Agent architecture

Sentinel MAS uses a **router + tool use** design pattern built on LangGraph,
with agent configuration following a CrewAI-inspired template style that
separates prompts from code.

### Intent routing

```
Incoming query
     │
     ▼
  Router node  ──── intent: TRACKING  ──▶  Tracking Agent
               ──── intent: EVENTS    ──▶  Event Agent
               ──── intent: SOP       ──▶  FAQ / SOP Agent
```

The router classifies the incoming message and dispatches to the appropriate
specialist agent. Each agent operates within a LangGraph subgraph and returns
its result to the orchestrator.

### Agent template pattern

Agents are defined declaratively via an `AGENT_REGISTRY`. Each entry specifies
the LLM model, temperature, system prompt, and available tools — no agent
logic is embedded in the prompt definition. This is the CrewAI-inspired
separation: configuration drives behaviour, code stays generic.

```
AGENT_REGISTRY["tracking"] = AgentRuntime(
    llm_model       = "gpt-4o-mini",
    llm_temperature = 0.0,
    system_prompt   = "...",
    tools           = { "get_position": tracking_tool }
)
```

### Sentinel policy (guardrail)

The policy layer sits between the orchestrator and tool execution. It enforces:

- **Authentication** — verifies the agent is authorised to call the requested tool
- **Authorisation** — validates the operation is permitted for the agent's role
- **Rate limiting** — prevents excessive tool calls within a time window
- **Access control** — blocks cross-agent tool access (e.g. FAQ agent cannot call tracking tools)

The guardrail operates at the infrastructure level, not in the prompt. An
agent that attempts to call an unauthorised tool receives a policy rejection
before the tool executes.

---

## Data flow

```
1. External trigger (CloudWatch alarm / operator query / API call)
        │
        ▼
2. SQS queue  ←────────────────────────────────────────────┐
        │                                                   │
        ▼                                                   │
3. Central agent — classifies intent, routes to specialist  │
        │                                                   │
        ▼                                                   │
4. Specialist agent — calls tools via Sentinel policy layer │
        │                                                   │
        ▼                                                   │
5. Tool executes (Sentinel Server / Events DB / Embedding DB)
        │
        ▼
6. Outcome written to RDS audit log
        │
        ▼
7. API service exposes result to UI / external consumers
```

---

## Deployment architecture

```
GitHub Actions (CI)
  └─▶ Build Docker images
  └─▶ Push to ECR
  └─▶ Register new ECS task definition
  └─▶ Trigger CodeDeploy deployment

CodeDeploy (blue/green)
  └─▶ Start green tasks alongside blue
  └─▶ Shift 10% canary traffic to green
  └─▶ Monitor CloudWatch alarms for 10 minutes
  └─▶ If healthy → shift 100% to green, terminate blue
  └─▶ If unhealthy → automatic rollback to blue
```

Two ALB target groups (`blue` and `green`) exist at all times. CodeDeploy
manages traffic weight between them. The active colour swaps on each deployment.

---

## Key design decisions

See `docs/adr/` for full decision records. Summary:

**ECS over Kubernetes** — operational overhead not justified at current team
size. ECS Fargate eliminates node management entirely.

**SQS over Redis** — avoids a stateful service. At-least-once delivery is
acceptable for the remediation use case; idempotency is enforced in agents.

**RDS PostgreSQL** — JSONB columns provide document-store flexibility for
agent state without introducing a separate database engine.

**Sentinel policy as infrastructure, not prompt** — guardrails enforced at
the tool call boundary are harder to circumvent than prompt-level instructions.
They also produce auditable rejection records.

**CrewAI-style agent templates** — separating prompts from code makes agents
testable in isolation and allows non-engineers to tune behaviour without
touching Python.

---

## Directory structure

```
sentinel-mas/
├── .claude/
│   └── commands/           # Claude Code workflow commands
│       ├── feature-spec.md
│       ├── changelog.md
│       └── init-specs.md
├── services/
│   ├── api/                # FastAPI service
│   ├── ui/                 # React operator dashboard
│   └── central/            # Orchestrator + agent registry
│       ├── agents/
│       │   ├── crew_agents.py   # Agent template definitions
│       │   └── crew.py          # LangGraph graph compilation
│       ├── state/
│       │   └── graph_state.py   # Shared TypedDict state schema
│       └── policy/
│           └── sentinel_policy.py  # Tool access guardrail
├── infra/
│   └── terraform/
│       ├── modules/        # networking, iam, rds, alb, ecs, codedeploy
│       └── environments/   # dev, prod
├── specs/                  # Living project constitution
│   ├── mission.md
│   ├── tech-stack.md
│   └── roadmap.md
└── docs/                   # This folder
```
