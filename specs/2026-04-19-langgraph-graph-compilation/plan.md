# Plan — Phase 6: LangGraph Graph Compilation

---

## 1. Verify LangGraph installation

1.1 Run `py -3.11 -c "import langgraph; print(langgraph.__version__)"` to
    confirm the package is available.
1.2 Check the correct import path for `StateGraph`, `START`, `END`, and the
    compiled graph type — these may vary by LangGraph version.
1.3 If not installed: `pip install langgraph` (no new external dependency —
    already declared in `specs/tech-stack.md`).

---

## 2. Implement `crew.py`

2.1 Create `services/central/crew.py`:
   - Import `StateGraph`, `START`, `END` from `langgraph.graph`
   - Import `GraphState` from `services.central.state`
   - Import `router_node` from `services.central.router`
   - Import `tracking_node`, `events_node`, `faq_node` from
     `services.central.agents`
   - Define `_route(state: GraphState) -> str` routing function
   - Define `build_graph()` that:
     1. Creates `StateGraph(GraphState)`
     2. Adds nodes: `"router"`, `"tracking"`, `"events"`, `"faq"`
     3. Adds edge `START → "router"`
     4. Adds conditional edges from `"router"` using `_route` and the
        intent→node mapping
     5. Adds edges from each agent node to `END`
     6. Returns `graph.compile()`
   - Define module-level `SENTINEL_GRAPH = build_graph()`

---

## 3. Tests (`test_crew.py`)

3.1 Create `services/central/tests/test_crew.py`.
3.2 Write smoke tests covering:
   - TRACKING query: `graph.invoke(make_state("where is vessel X"))` →
     `state["intent"] == "TRACKING"`, `state["agent_result"]` is not None,
     `state["error"] is None`
   - EVENTS query → `state["intent"] == "EVENTS"`, result present
   - SOP query → `state["intent"] == "SOP"`, result present
   - Unknown query → `state["error"]` is non-empty, `state["intent"]` is None
3.3 Each test uses `build_graph()` for a fresh graph instance (not the
    module-level `SENTINEL_GRAPH`) to ensure test isolation.

---

## 4. Update roadmap

4.1 Mark the deferred Phase 4 item as done:
    `[ ] Wire router output to conditional edges` → `[x]`
