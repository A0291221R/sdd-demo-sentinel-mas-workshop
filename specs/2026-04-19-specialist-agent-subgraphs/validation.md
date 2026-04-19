# Validation — Phase 5: Specialist Agent Subgraphs

---

## Automated

### Unit tests (`services/central/tests/test_subgraph_nodes.py`)

| # | Test case | Assertion |
|---|-----------|-----------|
| 1 | `tracking_node` called with fresh state | `state["agent_result"] == {"lat": 0.0, "lon": 0.0, "vessel": "stub"}` |
| 2 | `tracking_node` appends audit entry | `len(state["audit_log"]) == 1` |
| 3 | `events_node` called with fresh state | `state["agent_result"] == [{"event": "stub", "severity": "low"}]` |
| 4 | `faq_node` called with fresh state | `state["agent_result"] == {"answer": "stub SOP response"}` |
| 5 | Cross-agent: tracking node with events tool | `state["error"]` is non-empty; `state["agent_result"]` is `None` |
| 6 | `NODE_MAP` covers all three `Intent` values | `set(NODE_MAP.keys()) == {"TRACKING", "EVENTS", "SOP"}` |

### Integration tests (`services/central/tests/test_integration.py`)

| # | Query | Expected intent | Expected `agent_result` key |
|---|-------|----------------|---------------------------|
| 1 | `"where is vessel IMO-001"` | `TRACKING` | `{"lat": ..., "lon": ..., "vessel": ...}` |
| 2 | `"show me recent alerts"` | `EVENTS` | list with `"event"` key |
| 3 | `"what is the procedure for X"` | `SOP` | `{"answer": ...}` |

Each integration test also asserts:
- `state["error"] is None`
- `len(state["audit_log"]) >= 1`

### Type check

```
mypy services/central/agents/subgraph_nodes.py --strict --explicit-package-bases
```

Must pass with zero errors.

---

## Manual

1. Run unit tests: `py -3.11 -m pytest services/central/tests/test_subgraph_nodes.py -v`
2. Run integration tests: `py -3.11 -m pytest services/central/tests/test_integration.py -v`
3. Confirm `tracking_node` is importable:
   `python -c "from services.central.agents import tracking_node; print('ok')"`

---

## Definition of done

- [ ] `AgentNode` dataclass defined in `subgraph_nodes.py`
- [ ] `tracking_node`, `events_node`, `faq_node` module-level instances exist
- [ ] `NODE_MAP` covers all three `Intent` keys
- [ ] `agents/__init__.py` exports all new symbols
- [ ] Cross-agent policy rejection test passes
- [ ] End-to-end integration test passes for all three intents
- [ ] `mypy --strict` passes on `subgraph_nodes.py`
