# Validation — Phase 6: LangGraph Graph Compilation

---

## Automated

### Smoke tests (`services/central/tests/test_crew.py`)

| # | Query | Assertion |
|---|-------|-----------|
| 1 | TRACKING query | `state["intent"] == "TRACKING"`, `state["agent_result"]` not None, `state["error"] is None` |
| 2 | EVENTS query | `state["intent"] == "EVENTS"`, `state["agent_result"]` not None, `state["error"] is None` |
| 3 | SOP query | `state["intent"] == "SOP"`, `state["agent_result"]` not None, `state["error"] is None` |
| 4 | Unknown query | `state["error"]` is non-empty, `state["intent"] is None` |

Each test calls `build_graph().invoke(make_state(query))` to get a fresh
graph per test.

### Type check

```
mypy services/central/crew.py --strict --explicit-package-bases
```

Must pass with zero errors.

---

## Manual

1. Run `py -3.11 -m pytest services/central/tests/test_crew.py -v`
2. Confirm 4 tests pass.
3. Confirm `SENTINEL_GRAPH` is importable:
   `python -c "from services.central.crew import SENTINEL_GRAPH; print('ok')"`
4. Run full test suite to confirm no regressions:
   `py -3.11 -m pytest services/central/tests/ -v`

---

## Definition of done

- [ ] `build_graph()` defined in `services/central/crew.py`
- [ ] `SENTINEL_GRAPH` module-level compiled graph exists
- [ ] Conditional edges route all three intents to correct agent nodes
- [ ] Unknown-intent path routes to END without raising
- [ ] All 4 smoke tests pass
- [ ] Full test suite (41 existing + 4 new = 45) passes with no regressions
- [ ] `mypy --strict` passes on `crew.py`
- [ ] Phase 4 deferred roadmap item marked `[x]`
