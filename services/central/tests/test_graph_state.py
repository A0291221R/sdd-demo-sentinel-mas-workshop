from __future__ import annotations

import operator
from typing import Optional

import pytest
from services.central.state import GraphState, Intent, make_state


def test_construct_with_query_only() -> None:
    state = GraphState(query="find ship IMO 1234567")
    assert state["query"] == "find ship IMO 1234567"
    assert "intent" not in state
    assert "agent_result" not in state
    assert "audit_log" not in state
    assert "error" not in state


def test_construct_with_all_fields() -> None:
    state = GraphState(
        query="find ship IMO 1234567",
        intent="TRACKING",
        agent_result={"position": {"lat": 1.23, "lon": 4.56}},
        audit_log=[],
        error=None,
    )
    assert state["query"] == "find ship IMO 1234567"
    assert state["intent"] == "TRACKING"
    assert state["agent_result"] == {"position": {"lat": 1.23, "lon": 4.56}}
    assert state["audit_log"] == []
    assert state["error"] is None


def test_audit_log_reducer_merges_lists() -> None:
    """Verify operator.add is a valid reducer: two list chunks merge correctly."""
    existing: list[dict[str, object]] = [{"type": "tool_call", "tool": "get_position"}]
    new_event: list[dict[str, object]] = [{"type": "policy_rejection", "tool": "query_events"}]
    merged = operator.add(existing, new_event)
    assert len(merged) == 2
    assert merged[0]["type"] == "tool_call"
    assert merged[1]["type"] == "policy_rejection"


def test_make_state_provides_safe_defaults() -> None:
    state = make_state("find ship IMO 1234567")
    assert state["query"] == "find ship IMO 1234567"
    assert state["intent"] is None
    assert state["agent_result"] is None
    assert state["audit_log"] == []
    assert state["error"] is None


def test_make_state_audit_log_is_mutable() -> None:
    state = make_state("test")
    state["audit_log"].append({"type": "tool_call", "tool": "get_position"})
    assert len(state["audit_log"]) == 1


def test_error_accepts_none_and_string() -> None:
    state_none = GraphState(query="test", error=None)
    assert state_none["error"] is None

    state_msg = GraphState(query="test", error="upstream timeout")
    assert state_msg["error"] == "upstream timeout"


@pytest.mark.parametrize("intent", [None, "TRACKING", "EVENTS", "SOP"])
def test_intent_accepts_valid_values(intent: Optional[Intent]) -> None:
    state = GraphState(query="test", intent=intent)
    assert state["intent"] == intent
