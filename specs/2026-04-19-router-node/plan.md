# Plan — Phase 4: Router Node

---

## 1. State schema check

1.1 Read `services/central/state/graph_state.py` and confirm `intent` is
    typed as `Literal["TRACKING", "EVENTS", "SOP", ""]`.  
1.2 If the empty-string literal is missing, add it to keep `make_state()`
    valid (router writes intent; initial state has `""`).

---

## 2. Router module

2.1 Create `services/central/router/__init__.py` exporting `router_node`.  
2.2 Create `services/central/router/router_node.py`:
   - Define `INTENT_KEYWORDS: dict[str, list[str]]` with keys `"TRACKING"`,
     `"EVENTS"`, `"SOP"` and their keyword lists.
   - Implement `router_node(state: GraphState) -> GraphState`:
     - Lowercase `state["query"]`.
     - Iterate TRACKING → EVENTS → SOP; set `state["intent"]` on first match.
     - If no match, set `state["error"]`.
     - Return state.

---

## 3. Tests

3.1 Create `services/central/tests/test_router_node.py`.  
3.2 Write tests covering:
   - TRACKING intent matched (e.g. query `"where is vessel IMO-001"`)
   - EVENTS intent matched (e.g. query `"show me recent alerts"`)
   - SOP intent matched (e.g. query `"what is the SOP for breach response"`)
   - Unknown intent → `state["error"]` set, `state["intent"]` unchanged
   - Case-insensitivity (e.g. `"TRACK vessel"` → TRACKING)
   - First-match priority (query with both TRACKING and EVENTS keywords →
     TRACKING wins)
