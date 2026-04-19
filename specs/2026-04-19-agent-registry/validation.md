# Validation — Phase 3: Agent Registry and Base Runtime

_Branch: `phase-3-agent-registry` | Date: 2026-04-19_

---

## Automated

### Tests (pytest)

Run: `pytest services/central/tests/test_agent_executor.py -v`

Required assertions:
- `execute("tracking", "get_position", state)` sets `agent_result` to the stub dict and appends one `tool_call` entry to `audit_log`
- Same for `"events"` / `query_events` and `"faq"` / `search_sop`
- Cross-agent call sets `state["error"] == "not authorised"`, appends a rejection entry to `audit_log`, and does NOT overwrite `agent_result`
- Unknown agent name raises `KeyError`
- Unknown tool name (not in policy map) returns a policy rejection with `reason == "not authorised"` — not a `KeyError` (policy check precedes tool lookup)
- Tool exception logs a `tool_error` entry to `audit_log`, sets `state["error"]`, does not set `agent_result`
- Two sequential permitted calls accumulate two entries in `audit_log`

All tests must pass with zero failures and zero skips.

### Type checking (mypy)

Run: `mypy services/central/agents/ --strict`

Required: zero errors, zero warnings.

---

## Manual

1. Open `crew_agents.py` — confirm:
   - `AGENT_REGISTRY` has exactly three entries: `"tracking"`, `"events"`, `"faq"`
   - Each stub tool is a plain function (no mock framework)
   - `AgentRuntime` uses `@dataclass`, not `@dataclass(frozen=True)` — tools dict must remain replaceable

2. Open `agent_executor.py` — confirm:
   - `execute` appends to `state["audit_log"]` exactly once per call (either a rejection entry or a tool_call entry, never both)
   - `state["error"]` is only set on rejection — not touched on success
   - No LLM calls, no I/O, no imports beyond stdlib and Phase 1/2 modules

3. In a Python REPL, construct a policy + executor and call `execute` for each
   agent; confirm `audit_log` grows and `agent_result` reflects the stub return

---

## Definition of done

- [ ] `services/central/agents/crew_agents.py` exists with `AgentRuntime` and `AGENT_REGISTRY`
- [ ] `services/central/agents/agent_executor.py` exists with `AgentExecutor`
- [ ] All three agents have stub tools returning the correct fixture shapes
- [ ] `execute` steps match the spec order (lookup → policy → call → log → return)
- [ ] Policy rejection sets `error`, appends to `audit_log`, does NOT set `agent_result`
- [ ] Unknown agent raises `KeyError`; unknown tool returns policy rejection (not `KeyError`)
- [ ] All pytest assertions pass
- [ ] `mypy --strict` zero errors on `services/central/agents/`
- [ ] `specs/roadmap.md` Phase 3 items checked off
