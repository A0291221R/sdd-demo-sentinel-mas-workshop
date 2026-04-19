# Requirements — Phase 4: Router Node

_Branch: `phase-4-router-node` | Date: 2026-04-19_

---

## Scope

### Included

Implement `router_node` — a LangGraph-compatible node function that reads
`GraphState["query"]`, classifies it into one of three intents
(`TRACKING`, `EVENTS`, `SOP`) using keyword matching, and writes the
result back to `GraphState["intent"]`. On unrecognised input it sets
`GraphState["error"]` and returns state unchanged.

### Not included

- No real LLM call — classification is keyword-based only
- No conditional edge wiring — edges are deferred to Phase 6 (graph
  compilation)
- No integration with specialist agent subgraphs — those are Phase 5
- No persistence of the classified intent

---

## Data shapes

### Input / Output

The router node signature follows the LangGraph node contract:

```python
def router_node(state: GraphState) -> GraphState
```

Reads: `state["query"]` (str)  
Writes: `state["intent"]` on success, `state["error"]` on failure

### Intent values

| Intent | Description | Example keywords |
|--------|-------------|-----------------|
| `"TRACKING"` | Vessel position / location queries | `position`, `location`, `track`, `vessel`, `where`, `lat`, `lon` |
| `"EVENTS"` | Security event / alert queries | `event`, `alert`, `alarm`, `incident`, `severity`, `breach` |
| `"SOP"` | Procedure / FAQ / runbook queries | `sop`, `procedure`, `faq`, `how to`, `protocol`, `guide`, `runbook` |

Classification is case-insensitive; first match wins in the order
TRACKING → EVENTS → SOP.

### Error case

When no keyword matches:

```python
state["error"] = f"Router could not classify intent for query: {state['query']!r}"
```

`state["intent"]` is left at its current value (empty string from `make_state()`).

---

## Decisions

**Keyword matcher, not LLM**  
Consistent with Phase 3's no-real-LLM-calls constraint. The keyword list
can be replaced by an LLM call in a later phase without changing the node
signature or tests.

**Set error, return state on unknown intent**  
Consistent with how `AgentExecutor` handles policy rejections: always
return a valid `GraphState`, never raise. The caller decides what to do
with a non-empty `error` field.

**Intent only, no conditional edges**  
Conditional edges require the specialist subgraphs (Phase 5) and the
compiled graph (Phase 6). The router's responsibility ends at writing
`intent` to state.

**First-match ordering: TRACKING → EVENTS → SOP**  
Specificity order — tracking and event queries tend to be more precise;
SOP is a reasonable fallback category but is not a default catch-all.

---

## Context

- File locations:
  - `services/central/router/__init__.py` — exports
  - `services/central/router/router_node.py` — `router_node` function and `INTENT_KEYWORDS` map
- Test location: `services/central/tests/test_router_node.py`
- No new dependencies — stdlib + Phase 1 module only
- Import pattern: `from services.central.state import GraphState, make_state`
- Follow LangGraph node convention: pure function, takes and returns `GraphState`
- `GraphState["intent"]` is typed as `Literal["TRACKING", "EVENTS", "SOP", ""]`
  (defined in Phase 1 — confirm in `services/central/state/graph_state.py`)
