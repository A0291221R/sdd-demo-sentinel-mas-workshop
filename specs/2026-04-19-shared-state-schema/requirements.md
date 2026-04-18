# Requirements — Phase 1: Shared State Schema

_Branch: `phase-1-shared-state-schema` | Date: 2026-04-19_

---

## Scope

### Included

Define the `GraphState` TypedDict that is passed between every node in the
LangGraph graph: the router, all specialist agent subgraphs, and any future
nodes. This is the single source of truth for what data flows through the
orchestrator.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | `str` | Yes | Raw incoming natural language query from operator or SQS |
| `intent` | `NotRequired[str \| None]` | No | Classified intent — `TRACKING`, `EVENTS`, or `SOP`; set by the router |
| `agent_result` | `NotRequired[dict \| None]` | No | Structured output from whichever specialist agent handled the query |
| `audit_log` | `NotRequired[list[dict]]` | No | Append-only list of tool calls, policy rejections, and outcomes |
| `error` | `NotRequired[str \| None]` | No | Error message if any node or tool call fails |

### Not included

- No agent logic, tool definitions, or routing code (Phase 3+)
- No persistence / checkpointing to RDS (Phase 6)
- No validation of field values beyond type annotation — field content is
  validated at write time by the node that produces it

---

## Decisions

**`NotRequired[]` over `total=False` or split TypedDicts**
Python 3.11 supports `NotRequired` in a `total=True` TypedDict, which is
the most readable pattern: required fields are obvious by absence of the
annotation, optional fields are clearly marked. LangGraph reads state as a
dict and does not require a specific TypedDict shape, so this is compatible.

**`audit_log` default is an empty list**
Nodes append to `audit_log` rather than replacing it. LangGraph merges state
with `operator.add` for list fields if configured; otherwise nodes must read
the current list and return the extended version. The default must be
initialised to `[]` not `None` to avoid `None + [event]` errors.

**`agent_result` is untyped `dict`**
Each specialist agent returns a different shape. Typing the union now would
require forward declarations to Phase 3+ agent modules. We use `dict` and
document the expected keys per agent in their respective phase specs.

---

## Context

- File location: `services/central/state/graph_state.py`
- Test location: `services/central/tests/test_graph_state.py`
- No external dependencies beyond Python 3.11 stdlib — `typing` and
  `typing_extensions` only if `NotRequired` import requires it (it is in
  `typing` from 3.11+)
- Pytest is the test runner; no fixtures required for this phase
- Follow the architecture doc naming: `GraphState` (not `State`, `AgentState`,
  etc.) — this name will be imported by every future node
