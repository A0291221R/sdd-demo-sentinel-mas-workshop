# Plan — Phase 3: Agent Registry and Base Runtime

_Branch: `phase-3-agent-registry` | Date: 2026-04-19_

---

## Group 1 — Directory scaffold

1. Create `services/central/agents/` with `__init__.py`

## Group 2 — `AgentRuntime` dataclass and `AGENT_REGISTRY`

2. Create `services/central/agents/crew_agents.py`
3. Import: `dataclass` from `dataclasses`; `Callable` from `typing`
4. Define `@dataclass AgentRuntime` with fields:
   - `llm_model: str`
   - `llm_temperature: float`
   - `system_prompt: str`
   - `tools: dict[str, Callable[..., object]]`
5. Define three stub tool functions (module-level, no arguments beyond `**kwargs`):
   - `_get_position(**kwargs: object) -> dict[str, object]` — returns `{"lat": 0.0, "lon": 0.0, "vessel": "stub"}`
   - `_query_events(**kwargs: object) -> list[dict[str, object]]` — returns `[{"event": "stub", "severity": "low"}]`
   - `_search_sop(**kwargs: object) -> dict[str, object]` — returns `{"answer": "stub SOP response"}`
6. Define `AGENT_REGISTRY: dict[str, AgentRuntime]` with entries:
   - `"tracking"`: `AgentRuntime(llm_model="gpt-4o-mini", llm_temperature=0.0, system_prompt="You are a vessel tracking agent.", tools={"get_position": _get_position})`
   - `"events"`: `AgentRuntime(llm_model="gpt-4o-mini", llm_temperature=0.0, system_prompt="You are a security events agent.", tools={"query_events": _query_events})`
   - `"faq"`: `AgentRuntime(llm_model="gpt-4o-mini", llm_temperature=0.0, system_prompt="You are a SOPs and procedures agent.", tools={"search_sop": _search_sop})`

## Group 3 — `AgentExecutor`

7. Create `services/central/agents/agent_executor.py`
8. Import: `dataclasses`; `GraphState` and `make_state` from `services.central.state`;
   `SentinelPolicy` and `PolicyRejection` from `services.central.policy`;
   `AgentRuntime` from `.crew_agents`
9. Define `class AgentExecutor` with `__init__(self, registry, policy)`:
   - `registry: dict[str, AgentRuntime]`
   - `policy: SentinelPolicy`
10. Implement `execute(self, agent_name, tool_name, state, **kwargs) -> GraphState`:
    - Step 1: `runtime = self._registry[agent_name]` (raises `KeyError` on unknown agent)
    - Step 2: `tool = runtime.tools[tool_name]` (raises `KeyError` on unknown tool)
    - Step 3: `rejection = self._policy.check(agent_name, tool_name)`
      - If not None: append `dataclasses.asdict(rejection)` to `state["audit_log"]`;
        set `state["error"] = rejection.reason`; return state
    - Step 4: `result = tool(**kwargs)`
    - Step 5: append `{"type": "tool_call", "agent": agent_name, "tool": tool_name}`
      to `state["audit_log"]`
    - Step 6: set `state["agent_result"] = result`; return state

## Group 4 — Exports

11. Export `AgentRuntime`, `AGENT_REGISTRY` from `crew_agents.py` and
    `AgentExecutor` from `agent_executor.py` via `services/central/agents/__init__.py`

## Group 5 — Unit tests

12. Create `services/central/tests/test_agent_executor.py`
13. Fixture: `SentinelPolicy` permitting all three agents on their own tools,
    no rate limits; `AgentExecutor` constructed with `AGENT_REGISTRY` and the policy
14. **Permit — tracking**: `execute("tracking", "get_position", state)` returns state
    with `agent_result == {"lat": 0.0, "lon": 0.0, "vessel": "stub"}` and one
    `tool_call` entry in `audit_log`
15. **Permit — events**: `execute("events", "query_events", state)` returns state
    with correct `agent_result` and `audit_log` entry
16. **Permit — faq**: `execute("faq", "search_sop", state)` returns state
    with correct `agent_result` and `audit_log` entry
17. **Policy rejection**: configure policy to block cross-agent access; call
    `execute("faq", "get_position", state)`; assert `state["error"] == "not authorised"`,
    `agent_result` absent or None, and one rejection entry in `audit_log`
18. **Unknown agent raises KeyError**: assert `execute("ghost", "get_position", state)`
    raises `KeyError`
19. **Unknown tool raises KeyError**: assert `execute("tracking", "nonexistent", state)`
    raises `KeyError`
20. **`audit_log` accumulates across calls**: call permit twice on the same state;
    assert `len(state["audit_log"]) == 2`
