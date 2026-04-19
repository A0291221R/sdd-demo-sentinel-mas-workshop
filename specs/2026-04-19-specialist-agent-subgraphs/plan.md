# Plan — Phase 5: Specialist Agent Subgraphs

---

## 1. Read existing code

1.1 Read `services/central/agents/crew_agents.py` — confirm `AGENT_REGISTRY`
    keys (`"tracking"`, `"events"`, `"faq"`) and tool names.
1.2 Read `services/central/agents/agent_executor.py` — confirm `AgentExecutor`
    constructor signature and `execute` method signature.
1.3 Read `services/central/policy/sentinel_policy.py` — confirm default
    `POLICY_MAP` and `SentinelPolicy` constructor.
1.4 Read `services/central/agents/__init__.py` — note current exports.

---

## 2. Implement `subgraph_nodes.py`

2.1 Create `services/central/agents/subgraph_nodes.py`:
   - Import `AgentExecutor`, `AGENT_REGISTRY` from `crew_agents`
   - Import `SentinelPolicy`, `POLICY_MAP` from `sentinel_policy`
   - Import `GraphState`, `Intent` from `state`
   - Define `@dataclass class AgentNode` with fields `executor`, `agent_name`,
     `tool_name` and a `__call__(self, state: GraphState) -> GraphState` method
   - Construct a module-level `_default_policy = SentinelPolicy(POLICY_MAP)`
   - Construct a module-level `_default_executor = AgentExecutor(AGENT_REGISTRY, _default_policy)`
   - Define `tracking_node`, `events_node`, `faq_node` as `AgentNode` instances
   - Define `NODE_MAP: dict[Intent, AgentNode]`

---

## 3. Update `agents/__init__.py`

3.1 Add exports: `AgentNode`, `tracking_node`, `events_node`, `faq_node`,
    `NODE_MAP`.

---

## 4. Unit tests (`test_subgraph_nodes.py`)

4.1 Create `services/central/tests/test_subgraph_nodes.py`:
   - Test `tracking_node` sets `state["agent_result"]` and appends to
     `state["audit_log"]`
   - Test `events_node` sets `state["agent_result"]` correctly
   - Test `faq_node` sets `state["agent_result"]` correctly
   - **Cross-agent test**: construct a custom `AgentNode` for `"tracking"`
     but pass `tool_name="query_events"` (an events tool) — confirm
     `state["error"]` is set (policy rejection) and `state["agent_result"]`
     is unchanged
   - Test `NODE_MAP` contains all three `Intent` keys

---

## 5. Integration test (`test_integration.py`)

5.1 Create `services/central/tests/test_integration.py`:
   - Parametrize over three query/intent/expected-result pairs:
     - TRACKING query → `tracking_node` → `agent_result` contains vessel stub
     - EVENTS query → `events_node` → `agent_result` contains event stub
     - SOP query → `faq_node` → `agent_result` contains SOP stub
   - Each test: call `router_node(state)`, then `NODE_MAP[state["intent"]](state)`,
     assert `agent_result` and `audit_log` non-empty, `error` is `None`
