# Validation — Phase 4: Router Node

---

## Automated

### Tests (`services/central/tests/test_router_node.py`)

All of the following must pass:

| # | Test case | Assertion |
|---|-----------|-----------|
| 1 | TRACKING keyword in query | `state["intent"] == "TRACKING"` |
| 2 | EVENTS keyword in query | `state["intent"] == "EVENTS"` |
| 3 | SOP keyword in query | `state["intent"] == "SOP"` |
| 4 | No matching keyword | `state["error"]` is non-empty, `state["intent"] is None` |
| 5 | Mixed case query | Intent correctly classified (case-insensitive) |
| 6 | First-match ordering | TRACKING wins over EVENTS when both keywords present |

### Type check

```
mypy services/central/router/ --strict
```

Must pass with zero errors.

---

## Manual

1. From the repo root, run `python -m pytest services/central/tests/test_router_node.py -v`.
2. Confirm all 6+ tests pass with green output.
3. Confirm `router_node` is importable: `python -c "from services.central.router import router_node; print('ok')"`.

---

## Definition of done

- [ ] `router_node` function exists in `services/central/router/router_node.py`
- [ ] `INTENT_KEYWORDS` covers all three intents
- [ ] Unknown query sets `state["error"]`; does not raise
- [ ] All tests pass
- [ ] `mypy --strict` passes on the router module
- [ ] `services/central/router/__init__.py` exports `router_node`
