# Roadmap

_Last updated: 2026-04-19_

Phases are ordered by dependency and risk. Each phase is independently
runnable and testable before the next begins. The core agent pipeline ships
first; infrastructure and UI follow once the intelligence layer is proven.

---

## Phase 1 — Shared state schema

- [x] Define `GraphState` TypedDict with all fields the orchestrator and
      agents share (query, intent, agent_result, audit_log, error)
- [x] Write unit tests asserting field types and default values

## Phase 2 — Sentinel policy layer

- [x] Implement `sentinel_policy.py` with agent-to-tool permission map
- [x] Add authentication check (agent identity from call context)
- [x] Add rate limiting (per-agent, per-tool, configurable window)
- [x] Return structured `PolicyRejection` on any violation
- [x] Write unit tests for permit, reject, and rate-limit paths

## Phase 3 — Agent registry and base runtime

- [x] Define `AgentRuntime` dataclass (llm_model, llm_temperature,
      system_prompt, tools)
- [x] Implement `AGENT_REGISTRY` with stub entries for Tracking, Events,
      and FAQ/SOP agents
- [x] Implement generic agent executor that reads from registry and calls
      tools through the Sentinel policy layer
- [x] Write unit tests for registry lookup and policy-gated tool dispatch

## Phase 4 — Router node

- [ ] Implement the router LangGraph node that classifies intent
      (TRACKING / EVENTS / SOP) from the incoming query
- [ ] Wire router output to conditional edges dispatching to agent subgraphs
- [ ] Write unit tests for each intent classification path

## Phase 5 — Specialist agent subgraphs

- [ ] Implement Tracking Agent subgraph with stub `get_position` tool
- [ ] Implement Event Agent subgraph with stub `query_events` tool
- [ ] Implement FAQ/SOP Agent subgraph with stub `search_sop` tool
- [ ] Verify policy layer correctly blocks cross-agent tool access
- [ ] Integration test: end-to-end query → router → agent → result

## Phase 6 — LangGraph graph compilation

- [ ] Compile the full graph in `crew.py` (START → router → agents → END)
- [ ] Add shared state checkpointing to RDS (agent state JSONB columns)
- [ ] Smoke test the compiled graph locally with `docker compose up`

## Phase 7 — FastAPI service

- [ ] Implement `POST /query` endpoint that enqueues to SQS and returns a
      task ID
- [ ] Implement `GET /result/{task_id}` endpoint that reads from RDS audit log
- [ ] Implement `GET /health` endpoint
- [ ] Auto-generate OpenAPI docs (FastAPI default)
- [ ] Write integration tests for all endpoints against a local Postgres

## Phase 8 — SQS consumer in `central`

- [ ] Implement SQS long-poll consumer that dequeues messages and invokes
      the LangGraph graph
- [ ] Write audit log record to RDS on every graph completion
- [ ] Handle at-least-once delivery (idempotency key on task ID)
- [ ] Test consumer against LocalStack or real SQS in dev

## Phase 9 — React operator dashboard

- [ ] Scaffold React 18 app with TypeScript
- [ ] Implement query input and result display components
- [ ] Implement audit log view (paginated table of past queries and outcomes)
- [ ] Wire to API service via fetch; handle loading and error states
- [ ] Smoke test against local API service

## Phase 10 — Terraform infrastructure (dev environment)

- [ ] `networking` module: VPC, subnets, security groups
- [ ] `iam` module: ECS task roles, CodeDeploy role, ECR access
- [ ] `rds` module: PostgreSQL 15 instance, schema migration
- [ ] `sqs` module: standard queue with DLQ
- [ ] `ecs` module: cluster, task definitions for all three services
- [ ] `alb` module: listener rules routing `/api/*` and `/*`
- [ ] `codedeploy` module: blue/green deployment group with 10-minute bake
- [ ] Apply to dev; verify `docker compose`-equivalent traffic flow

## Phase 11 — CI/CD pipeline

- [ ] GitHub Actions workflow: lint, test, build Docker images, push to ECR
- [ ] Trigger CodeDeploy deployment on merge to `main`
- [ ] Add CloudWatch alarms for error rate and policy rejection rate
- [ ] Verify automatic rollback triggers on alarm breach

## Phase 12 — Production environment and hardening

- [ ] Terraform `prod` workspace with separate state
- [ ] Secrets Manager entries for all prod credentials
- [ ] CloudWatch dashboard for agent throughput, error rate, policy rejections
- [ ] Load test at expected peak traffic; confirm Fargate autoscaling config
- [ ] Runbook review: confirm all on-call procedures match deployed topology

---

## Deferred

- Embedding / vector search for SOP agent (requires separate vector DB decision)
- Multi-agent collaboration (agents calling each other, not just the orchestrator)
- Webhook push for async result delivery (current model is poll-based)
- Multi-region deployment
