# Validation — Phase 1: Shared State Schema

_Branch: `phase-1-shared-state-schema` | Date: 2026-04-19_

---

## Automated

### Tests (pytest)

Run: `pytest services/central/tests/test_graph_state.py -v`

Required assertions:
- `GraphState(query="find ship IMO 1234567")` constructs without error
- Resulting dict contains `query` and does not contain `intent`, `agent_result`,
  `audit_log`, or `error` keys (TypedDict does not inject defaults)
- `GraphState(query="...", intent="TRACKING", agent_result={"position": ...}, audit_log=[], error=None)` constructs without error
- `audit_log` field holds a list; appending a dict to it produces a list of
  length 1
- `intent` accepts `None`, `"TRACKING"`, `"EVENTS"`, and `"SOP"`
- `error` accepts `None` and a non-empty string

All tests must pass with zero failures and zero skips.

### Type checking (mypy)

Run: `mypy services/central/state/graph_state.py --strict`

Required: zero errors, zero warnings.

---

## Manual

1. Open `services/central/state/graph_state.py` — confirm:
   - `query` has no `NotRequired` wrapper (it is required)
   - All other four fields are wrapped in `NotRequired`
   - No business logic, no imports beyond `typing`

2. Open `services/central/state/__init__.py` — confirm `GraphState` is
   exported so `from services.central.state import GraphState` works

3. Grep for `GraphState` in any future Phase 2+ stub files — confirm this
   module is the single definition (no duplicate TypedDicts)

---

## Definition of done

- [ ] `services/central/state/graph_state.py` exists and defines `GraphState`
- [ ] All 5 fields present with correct `NotRequired` annotation pattern
- [ ] `GraphState` exported from `services/central/state/__init__.py`
- [ ] All pytest assertions pass
- [ ] `mypy --strict` reports zero errors on `graph_state.py`
- [ ] `specs/roadmap.md` Phase 1 items checked off
