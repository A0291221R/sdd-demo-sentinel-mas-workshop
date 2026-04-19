# Changelog

All notable changes to Sentinel MAS are documented here.
Entries are created automatically by `/feature-spec` and closed by `/changelog`.

## Unreleased

## 2026-04-19

### phase-8-sqs-consumer
- Branch: `phase-8-sqs-consumer`
- Spec: `specs/2026-04-19-sqs-consumer/`
- Status: merged
- Summary: Implements SQS long-poll consumer (consume_one + run_consumer) in services/central, wires POST /query to enqueue via SQS, adds pydantic-settings queue_url config, idempotency guard, and 9 consumer tests; RDS persistence and LocalStack testing deferred to Phase 10.

## 2026-04-19

### phase-7-fastapi-service
- Branch: `phase-7-fastapi-service`
- Spec: `specs/2026-04-19-fastapi-service/`
- Status: merged
- Summary: Implements services/api/ with POST /query (202, synchronous SENTINEL_GRAPH invocation), GET /result/{task_id} (200/404), and GET /health; in-memory task store with serialized agent_result; 10 TestClient tests; SQS and RDS wiring deferred to Phase 8.

## 2026-04-19

### phase-6-langgraph-graph-compilation
- Branch: `phase-6-langgraph-graph-compilation`
- Spec: `specs/2026-04-19-langgraph-graph-compilation/`
- Status: merged
- Summary: Compiles the full LangGraph StateGraph in crew.py (START → router → conditional edges → tracking/events/faq → END); exposes SENTINEL_GRAPH module-level singleton and build_graph() factory; fulfils Phase 4 deferred conditional-edge wiring. 50 tests, mypy strict clean.

## 2026-04-19

### phase-5-specialist-agent-subgraphs
- Branch: `phase-5-specialist-agent-subgraphs`
- Spec: `specs/2026-04-19-specialist-agent-subgraphs/`
- Status: merged
- Summary: Implements AgentNode frozen dataclass and three module-level specialist nodes (tracking, events, faq) that delegate to AgentExecutor for policy enforcement and audit logging; NODE_MAP wires Intent to callable node for Phase 6 graph compilation.

## 2026-04-19

### phase-4-router-node
- Branch: `phase-4-router-node`
- Spec: `specs/2026-04-19-router-node/`
- Status: merged
- Summary: Implements router_node that classifies natural language queries into TRACKING, EVENTS, or SOP intents using case-insensitive keyword matching, sets error on unrecognised input, and centralises the Intent type in GraphState.

## 2026-04-19

### phase-3-agent-registry
- Branch: `phase-3-agent-registry`
- Spec: `specs/2026-04-19-agent-registry/`
- Status: merged
- Summary: Implements AgentRuntime dataclass, AGENT_REGISTRY with three stub specialist agents, and AgentExecutor that looks up agents, enforces Sentinel policy, and appends outcomes to GraphState.audit_log — wiring Phase 1 state and Phase 2 policy into executable agent behaviour.

### phase-2-sentinel-policy-layer — 2026-04-19
- Branch: `phase-2-sentinel-policy-layer`
- Spec: `specs/2026-04-19-sentinel-policy-layer/`
- Status: merged
- Summary: Implements SentinelPolicy with frozen policy_map, per-agent/per-tool sliding-window rate limiting, threading.Lock on the prune/check/append sequence, and UTC-aware PolicyRejection. 11 tests, mypy strict clean.

### phase-1-shared-state-schema — 2026-04-19
- Branch: `phase-1-shared-state-schema`
- Spec: `specs/2026-04-19-shared-state-schema/`
- Status: merged
- Summary: Defined `GraphState` TypedDict with `operator.add` reducer on `audit_log`, `Literal` type for `intent`, and `make_state()` factory for safe initialisation. 10 tests, mypy strict clean.

<!-- feature entries will appear here -->
