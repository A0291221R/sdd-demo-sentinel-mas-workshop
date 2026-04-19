# Requirements — Phase 5: Specialist Agent Subgraphs

_Branch: `phase-5-specialist-agent-subgraphs` | Date: 2026-04-19_

---

## Scope

### Included

Implement three specialist agent node callables — `TrackingNode`, `EventsNode`,
`FaqNode` — that follow the same LangGraph node contract as `router_node`
(Phase 4): `(state: GraphState) -> GraphState`. Each node delegates to the
existing `AgentExecutor` (Phase 3) for policy enforcement and audit logging.

Also implement an end-to-end integration test that chains `router_node` →
correct specialist node for all three intents, and a cross-agent policy test
that confirms the policy layer blocks a node from calling another agent's tool.

### Not included

- No real LLM calls — tools remain the Phase 3 stubs
- No LangGraph graph compilation or conditional edges (Phase 6)
- No RDS persistence (Phase 6)
- No FastAPI or SQS integration (Phases 7–8)

---

## Data shapes

### `AgentNode`

A single generic class that closes over an `AgentExecutor`, an `agent_name`,
and a `tool_name`. Calling it acts as a LangGraph node.

```python
@dataclass
class AgentNode:
    executor: AgentExecutor
    agent_name: str
    tool_name: str

    def __call__(self, state: GraphState) -> GraphState:
        return self.executor.execute(self.agent_name, self.tool_name, state)
```

### Module-level node instances

Three pre-built instances constructed from the shared `AGENT_REGISTRY` and a
default `SentinelPolicy`. These are the objects Phase 6 will wire into the
compiled graph as nodes.

| Instance | `agent_name` | `tool_name` |
|----------|-------------|-------------|
| `tracking_node` | `"tracking"` | `"get_position"` |
| `events_node` | `"events"` | `"query_events"` |
| `faq_node` | `"faq"` | `"search_sop"` |

### Node dispatch map

A `NODE_MAP: dict[Intent, AgentNode]` that maps each intent value to its node
instance. Phase 6 uses this to wire conditional edges; the integration test uses
it to route without a compiled graph.

```python
NODE_MAP: dict[Intent, AgentNode] = {
    "TRACKING": tracking_node,
    "EVENTS":   events_node,
    "SOP":      faq_node,
}
```

---

## Decisions

**Single `AgentNode` class, not three separate classes**
All three nodes have identical logic — delegate to `AgentExecutor` with a
specific `agent_name`/`tool_name`. A single generic class avoids duplication
and keeps the pattern extensible: adding a fourth agent requires only a new
registry entry and a new `AgentNode(executor, "name", "tool")` line.

**Delegate to `AgentExecutor`, not direct tool calls**
`AgentExecutor` owns policy enforcement and audit log writes. Bypassing it in
Phase 5 would duplicate those concerns and break the "auditability by default"
principle from `specs/mission.md`.

**Plain callable (`__call__`), not a standalone function**
Nodes need an injected `AgentExecutor` (which requires `registry` + `policy`).
A callable dataclass is the cleanest way to bind dependencies while satisfying
the LangGraph node signature `(state: GraphState) -> GraphState`. Consistent
with Phase 3's constructor-injection pattern.

**Module-level default instances**
Phase 6 imports `tracking_node`, `events_node`, `faq_node` directly to wire
the graph. Constructing them at module load (with default policy) keeps Phase 6
imports simple. Tests that need a custom policy construct `AgentNode` directly.

**`NODE_MAP` keyed by `Intent`**
Provides a single place for Phase 6 to look up the right node from a classified
intent, and lets the integration test drive all three paths in a loop without
hardcoding conditionals.

---

## Context

- File locations:
  - `services/central/agents/subgraph_nodes.py` — `AgentNode`, `tracking_node`,
    `events_node`, `faq_node`, `NODE_MAP`
  - `services/central/agents/__init__.py` — add exports for the above
- Test locations:
  - `services/central/tests/test_subgraph_nodes.py` — unit + cross-agent tests
  - `services/central/tests/test_integration.py` — end-to-end integration test
- No new dependencies — stdlib + Phase 1/2/3/4 modules only
- Import pattern:
  - `from services.central.agents import AgentNode, tracking_node, events_node, faq_node, NODE_MAP`
  - `from services.central.agents import AGENT_REGISTRY, AgentExecutor`
  - `from services.central.policy import SentinelPolicy`
  - `from services.central.router import router_node`
- Follow `@dataclass` + constructor-injection pattern from Phases 2–3
- `SentinelPolicy` default policy for module-level instances: use the same
  `POLICY_MAP` already defined in `services/central/policy/sentinel_policy.py`
