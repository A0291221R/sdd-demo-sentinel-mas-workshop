# Requirements — Phase 6: LangGraph Graph Compilation

_Branch: `phase-6-langgraph-graph-compilation` | Date: 2026-04-19_

---

## Scope

### Included

Compile the full LangGraph `StateGraph` in `services/central/crew.py`:
`START → router_node → conditional edges → [tracking|events|faq] node → END`.

Expose a module-level `SENTINEL_GRAPH` (compiled runnable) and a
`build_graph()` factory for tests that need a fresh instance.

Write a pytest smoke test that calls `SENTINEL_GRAPH.invoke(...)` for each
of the three intents and asserts the final `GraphState` is correct.

### Not included

- No RDS checkpointing — deferred to Phase 7/8 when infrastructure exists
- No FastAPI or SQS integration — Phase 7/8
- No real LLM calls — tools remain Phase 3 stubs
- No `docker compose` smoke test — not meaningful without Phase 7/10 infra

---

## Graph structure

```
START
  │
  ▼
router_node          ← classifies state["intent"]
  │
  ├─ "TRACKING" ──▶ tracking_node ──▶ END
  ├─ "EVENTS"   ──▶ events_node   ──▶ END
  ├─ "SOP"      ──▶ faq_node      ──▶ END
  └─ "__error__" ─▶ END            ← router set state["error"], no intent
```

### Routing function

```python
def _route(state: GraphState) -> str:
    intent = state.get("intent")
    if intent in ("TRACKING", "EVENTS", "SOP"):
        return intent
    return "__error__"
```

The routing function returns an `Intent` string used as a key in the
conditional-edges mapping. The `"__error__"` sentinel routes directly to
`END` when the router could not classify the query.

### Conditional edges mapping

```python
{
    "TRACKING":  "tracking",
    "EVENTS":    "events",
    "SOP":       "faq",
    "__error__": END,
}
```

### Node names

| LangGraph node name | Callable |
|---------------------|----------|
| `"router"` | `router_node` (Phase 4) |
| `"tracking"` | `tracking_node` (Phase 5) |
| `"events"` | `events_node` (Phase 5) |
| `"faq"` | `faq_node` (Phase 5) |

---

## Public API

### `build_graph() -> CompiledGraph`

Constructs and compiles a fresh `StateGraph(GraphState)` every call.
Used by tests that need an isolated graph instance.

### `SENTINEL_GRAPH`

Module-level compiled graph built once at import time via `build_graph()`.
Phase 7/8 imports this to invoke the graph per SQS message.

---

## Decisions

**`build_graph()` factory + module-level singleton**
Tests need fresh graph instances (no shared state between test runs).
Phase 7 needs a single process-wide compiled graph. Both are satisfied by
exposing the factory and calling it once at module level.

**`"__error__"` sentinel for unclassified queries**
LangGraph conditional edges require every return value of the routing
function to appear as a key in the edge map. Returning `END` directly is
supported by LangGraph. The sentinel name makes the intent explicit in the
edge definition.

**RDS checkpointing deferred**
LangGraph's `MemorySaver` or Postgres checkpointer requires an active DB
connection. At this phase there is no provisioned RDS instance. Wiring the
checkpointer here would require mocking infrastructure, adding complexity
with no value. Phase 8 adds the SQS consumer that will pass a checkpointer
at invocation time.

**No conditional edge wiring deferred from Phase 4**
Phase 4's deferred roadmap item ("Wire router output to conditional edges")
is fulfilled here — it required the compiled graph, which is now the
explicit goal of Phase 6.

---

## Context

- File locations:
  - `services/central/crew.py` — `build_graph`, `SENTINEL_GRAPH`
- Test location: `services/central/tests/test_crew.py`
- New dependency: `langgraph` — already declared in tech stack; confirm
  it is installed in the Python 3.11 environment before implementing
- Import pattern:
  - `from langgraph.graph import StateGraph, START, END`
  - `from services.central.state import GraphState`
  - `from services.central.router import router_node`
  - `from services.central.agents import tracking_node, events_node, faq_node`
- LangGraph node contract: each node is `Callable[[GraphState], GraphState]`
  — all Phase 4/5 nodes already satisfy this
- `CompiledGraph` return type from `graph.compile()` — use
  `langgraph.graph.CompiledStateGraph` or `Any` if the type is not exported
