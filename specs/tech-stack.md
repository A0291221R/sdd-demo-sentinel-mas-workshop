# Tech Stack

_Last updated: 2026-04-19_

## Languages

| Language | Version | Used for |
|----------|---------|----------|
| Python | 3.11 | `central` orchestrator, `api` service |
| TypeScript | 5.x | `ui` React dashboard |

## Frameworks and libraries

| Library / Framework | Purpose |
|---------------------|---------|
| LangGraph | Agent graph compilation and execution for the `central` orchestrator |
| FastAPI | REST API service (`api`) — OpenAPI docs auto-generated |
| React 18 | Operator dashboard (`ui`) |
| Pydantic | Data validation and schema definition across Python services |

## Infrastructure (AWS-only)

| Component | Service | Reason |
|-----------|---------|--------|
| Compute | ECS Fargate | Eliminates node management; native AWS integrations |
| Load balancing | ALB | Routes `/api/*` → API service, `/*` → UI |
| Database | RDS PostgreSQL 15 | JSONB for agent state; audit log; task queue |
| Message queue | SQS (standard) | Decouples event sources from orchestrator; at-least-once delivery |
| Deployments | CodeDeploy (blue/green) | 10-minute canary bake; automatic rollback on alarm |
| Secrets | Secrets Manager | Injected into ECS task environment at launch |
| Container registry | ECR | Co-located with ECS |
| IaC | Terraform 1.6+ | Modular; dev and prod workspaces |

## Agent configuration pattern

Agents are declared in `AGENT_REGISTRY` (CrewAI-inspired template style).
Each entry is a plain data structure specifying `llm_model`, `llm_temperature`,
`system_prompt`, and `tools`. No agent logic lives in the declaration — the
runtime is fully generic.

## Deliberate exclusions

| Excluded | Reason |
|----------|--------|
| Kubernetes / EKS | Operational overhead not justified for a 2–3 person team at current scale |
| Redis | Avoided as a stateful dependency; SQS covers the queue use case |
| Separate vector DB | Not required for current agent tool set; revisit if embedding search is added |
| Prompt-level access control | Unreliable security boundary; all access control is in `sentinel_policy.py` |
| Multi-cloud abstractions | AWS-only; portability is an explicit non-goal |

## Local development

| Tool | Purpose |
|------|---------|
| Docker Desktop 24+ | Runs the full stack locally via `docker compose up` |
| Node.js 20 LTS | UI build toolchain |
| AWS CLI 2.x | Deployment commands |
| make | Convenience targets (`setup`, `test`, `lint`) |
