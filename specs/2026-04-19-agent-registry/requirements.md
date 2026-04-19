# Requirements — Phase 3: Agent Registry and Base Runtime

_Branch: `phase-3-agent-registry` | Date: 2026-04-19_

---

## Scope

### Included

Define `AgentRuntime` (the per-agent config dataclass), populate `AGENT_REGISTRY`
with stub entries for the three specialist agents, and implement the generic
`AgentExecutor` that looks up an agent from the registry, checks policy, calls
the tool, and appends the outcome to `GraphState.audit_log`.

This is the layer that wires Phase 1 (state) and Phase 2 (policy) together into
executable agent behaviour — without yet building the LangGraph graph (Phase 6).

### Not included

- No real LLM calls — tools are stubs that return fixture data
- No LangGraph node or graph wiring (Phase 4–6)
- No RDS persistence (Phase 6)
- No FastAPI or SQS integration (Phases 7–8)

---

## Data shapes

### `AgentRuntime`

| Field | Type | Description |
|-------|------|-------------|
| `llm_model` | `str` | LLM model identifier, e.g. `"gpt-4o-mini"` |
| `llm_temperature` | `float` | Sampling temperature, e.g. `0.0` for deterministic |
| `system_prompt` | `str` | Fixed system prompt defining the agent's role |
| `tools` | `dict[str, Callable[..., object]]` | Tool name → tool function |

### `AGENT_REGISTRY`

Module-level `dict[str, AgentRuntime]` with three stub entries:

| Key | Agent | Tool | Stub return |
|-----|-------|------|-------------|
| `"tracking"` | Tracking Agent | `get_position` | `{"lat": 0.0, "lon": 0.0, "vessel": "stub"}` |
| `"events"` | Event Agent | `query_events` | `[{"event": "stub", "severity": "low"}]` |
| `"faq"` | FAQ/SOP Agent | `search_sop` | `{"answer": "stub SOP response"}` |

### `AgentExecutor`

Constructor arguments:

| Argument | Type | Description |
|----------|------|-------------|
| `registry` | `dict[str, AgentRuntime]` | The agent registry to look up from |
| `policy` | `SentinelPolicy` | The shared policy instance; one per process |

Public interface:

| Method | Signature | Returns |
|--------|-----------|---------|
| `execute` | `(agent_name: str, tool_name: str, state: GraphState, **kwargs: object) -> GraphState` | Updated state with `agent_result` and appended `audit_log` entry |

`execute` steps in order:
1. Look up `agent_name` in `registry` → `KeyError` if unknown (programming error, not a policy rejection)
2. Look up `tool_name` in `runtime.tools` → `KeyError` if unknown
3. Call `policy.check(agent_name, tool_name)`:
   - If rejected: append `dataclasses.asdict(rejection)` to `state["audit_log"]`; set `state["error"]` to `rejection.reason`; return state
4. Call `runtime.tools[tool_name](**kwargs)` → result
5. Append `{"type": "tool_call", "agent": agent_name, "tool": tool_name}` to `state["audit_log"]`
6. Set `state["agent_result"]` to the tool result; return state

---

## Decisions

**`AgentRuntime` as a `@dataclass`**
Consistent with Phase 2 (`RateLimit`, `PolicyRejection`). No serialisation needed
at this layer — runtime objects live in memory only. Pydantic deferred to Phase 7.

**Stub tools as plain functions, not mocks**
Stub functions return fixed dicts without any mock framework. This keeps tests
simple, removes the `unittest.mock` dependency, and lets the stubs later be
replaced by real implementations with zero test-structure changes.

**`AgentExecutor` receives `GraphState` and returns updated `GraphState`**
The executor is responsible for both calling the tool and recording the outcome
in state. This keeps all audit-log mutation in one place and makes the LangGraph
node wrapper (Phase 4+) trivial: it just calls `executor.execute(...)` and
returns the result.

**`KeyError` on unknown agent or tool, not `PolicyRejection`**
An unknown agent/tool name passed to `execute` is a programming error — it means
the caller is misconfigured. Policy rejections are operational (authorisation
failures at runtime). These two failure modes must not be conflated.

**One shared `SentinelPolicy` instance**
Phase 2 established that rate-limit counters are per-instance. `AgentExecutor`
receives the policy via constructor injection; callers must share one instance
across all executors to get process-wide rate limiting.

---

## Context

- File locations:
  - `services/central/agents/crew_agents.py` — `AgentRuntime`, `AGENT_REGISTRY`
  - `services/central/agents/agent_executor.py` — `AgentExecutor`
  - `services/central/agents/__init__.py` — exports
- Test location: `services/central/tests/test_agent_executor.py`
- No new dependencies — stdlib + Phase 1/2 modules only
- Import pattern: `from services.central.state import GraphState, make_state`
  and `from services.central.policy import SentinelPolicy, PolicyRejection, RateLimit`
- Follow existing `@dataclass` + module-level registry pattern from Phase 2
