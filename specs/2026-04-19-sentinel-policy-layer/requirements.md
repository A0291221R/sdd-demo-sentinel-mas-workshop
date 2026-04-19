# Requirements — Phase 2: Sentinel Policy Layer

_Branch: `phase-2-sentinel-policy-layer` | Date: 2026-04-19_

---

## Scope

### Included

Implement `SentinelPolicy` — the infrastructure-level guardrail that intercepts
every tool call before execution and enforces authorisation and rate limiting.
This is the security boundary described in `docs/adr/002-sentinel-policy-as-infrastructure.md`.

### Not included

- No integration with actual tool functions (Phase 3+ wires tools through policy)
- No persistence of rejection records to RDS (Phase 6)
- No distributed rate limiting — in-process sliding window only; one process
  per deployment is the current assumption
- No dynamic policy reload — changes require a code change and redeploy

---

## Data shapes

### `RateLimit`

| Field | Type | Description |
|-------|------|-------------|
| `max_calls` | `int` | Maximum number of calls allowed in the window |
| `window_seconds` | `int` | Rolling window duration in seconds |

### `PolicyRejection`

| Field | Type | Description |
|-------|------|-------------|
| `agent` | `str` | Identity of the agent that attempted the call |
| `tool` | `str` | Name of the tool that was blocked |
| `reason` | `str` | Human-readable rejection cause (see reasons below) |
| `timestamp` | `datetime` | UTC datetime when the rejection occurred |

**Canonical reason strings:**

| Reason | Trigger |
|--------|---------|
| `"unknown agent"` | Agent name not present in the policy map |
| `"not authorised"` | Agent is known but the tool is not in its allowed set |
| `"rate limit exceeded"` | Call count within the window exceeds `max_calls` |

### `SentinelPolicy`

Constructor arguments:

| Argument | Type | Description |
|----------|------|-------------|
| `policy_map` | `dict[str, set[str]]` | Agent name → set of allowed tool names |
| `rate_limits` | `dict[str, dict[str, RateLimit]]` | Agent name → tool name → `RateLimit` |

Public interface:

| Method | Signature | Returns |
|--------|-----------|---------|
| `check` | `(agent: str, tool: str) -> PolicyRejection \| None` | `None` if permitted; `PolicyRejection` if blocked |

`check` performs checks in this order:
1. Unknown agent → reject
2. Tool not in agent's allowed set → reject
3. Rate limit exceeded → reject
4. All pass → record the call timestamp and return `None`

---

## Decisions

**`dict[str, set[str]]` for the permission map**
Agent-keyed map mirrors how callers think: "what can the tracking agent do?"
It is also the simplest structure to extend — adding an agent or a tool is one
line. The alternative (tool-keyed) inverts the mental model without benefit.

**Dataclasses over Pydantic for `RateLimit` and `PolicyRejection`**
No serialisation is needed in this phase (rejection records are passed in-
process and appended to `GraphState.audit_log`). Pydantic adds no value over
stdlib `@dataclass` here. Pydantic will be introduced when cross-service
serialisation is needed (Phase 7, FastAPI).

**In-process sliding window for rate limiting**
Redis is deliberately excluded (see `specs/tech-stack.md`). A `deque` of
call timestamps per `(agent, tool)` pair provides an accurate sliding window
with O(1) amortised cost. Single-process deployment makes this safe for now.

**`SentinelPolicy` as an injectable class, not a module-level singleton**
Tests need to construct policies with different maps and limits without
monkey-patching globals. The class pattern also allows Phase 3+ to inject
the policy into the agent executor via dependency injection.

**`check` returns `None` on permit, `PolicyRejection` on block**
Callers branch on `if rejection := policy.check(agent, tool)` — the walrus
pattern makes the happy path (`None`) the default and the rejection the
named exception. A boolean return would lose the rejection details.

---

## Context

- File location: `services/central/policy/sentinel_policy.py`
- Test location: `services/central/tests/test_sentinel_policy.py`
- No new dependencies — stdlib only (`dataclasses`, `datetime`, `collections`)
- `PolicyRejection` will be appended to `GraphState.audit_log` by callers;
  it must be serialisable to `dict[str, object]` (use `dataclasses.asdict`)
- Follow Phase 1 pattern: class exported from `services/central/policy/__init__.py`
- `datetime.now(UTC)` requires `from datetime import datetime, timezone`;
  always use `datetime.now(timezone.utc)` — never naive datetimes
