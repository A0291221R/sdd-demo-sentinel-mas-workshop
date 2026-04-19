import pytest

from services.central.agents import NODE_MAP
from services.central.router import router_node
from services.central.state import make_state


@pytest.mark.parametrize(
    "query, expected_intent, result_key",
    [
        ("where is vessel IMO-001", "TRACKING", "vessel"),
        ("show me recent alerts for zone 3", "EVENTS", "event"),
        ("what is the procedure for safe boarding", "SOP", "answer"),
    ],
)
def test_end_to_end(query: str, expected_intent: str, result_key: str) -> None:
    state = make_state(query)

    state = router_node(state)
    assert state["intent"] == expected_intent
    assert state["error"] is None

    assert state["intent"] is not None
    agent_node = NODE_MAP[state["intent"]]
    state = agent_node(state)

    assert state["error"] is None
    assert state["agent_result"] is not None
    assert len(state["audit_log"]) >= 1

    result = state["agent_result"]
    if isinstance(result, dict):
        assert result_key in result
    elif isinstance(result, list):
        assert len(result) > 0
        assert result_key in result[0]
    else:
        raise AssertionError(f"Unexpected agent_result type: {type(result)}")
