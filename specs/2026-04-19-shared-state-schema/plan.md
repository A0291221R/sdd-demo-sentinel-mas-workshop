# Plan — Phase 1: Shared State Schema

_Branch: `phase-1-shared-state-schema` | Date: 2026-04-19_

---

## Group 1 — Directory scaffold

1. Create `services/central/` directory with `__init__.py`
2. Create `services/central/state/` directory with `__init__.py`
3. Create `services/central/tests/` directory with `__init__.py` and
   `conftest.py` (empty for now)

## Group 2 — `GraphState` TypedDict

4. Create `services/central/state/graph_state.py`
5. Import `TypedDict` and `NotRequired` from `typing` (Python 3.11+)
6. Define `GraphState(TypedDict)` with `total=True`:
   - `query: str` — required; no default
   - `intent: NotRequired[str | None]` — optional; default `None`
   - `agent_result: NotRequired[dict | None]` — optional; default `None`
   - `audit_log: NotRequired[list[dict]]` — optional; default `[]`
   - `error: NotRequired[str | None]` — optional; default `None`
7. Export `GraphState` from `services/central/state/__init__.py`

## Group 3 — Unit tests

8. Create `services/central/tests/test_graph_state.py`
9. Test: constructing `GraphState` with only `query` — assert all optional
   fields are absent (TypedDict does not set defaults; test that the dict
   does not contain keys not provided)
10. Test: constructing `GraphState` with all fields — assert each field
    holds the provided value and the correct type is accepted by the
    type checker
11. Test: `audit_log` field accepts a list of dicts and appending to it
    produces the expected extended list (verifies the append pattern
    nodes will use)
12. Test: `error` field accepts `None` and a non-empty string
13. Test: `intent` field accepts `None` and the three expected string
    values (`"TRACKING"`, `"EVENTS"`, `"SOP"`)

## Group 4 — Type checking

14. Add a minimal `pyproject.toml` or `mypy.ini` under `services/central/`
    if none exists, with `python_version = "3.11"` and
    `strict = true` (or equivalent flags)
15. Run `mypy services/central/state/graph_state.py` — confirm zero errors
