from services.central.agents import (
    AGENT_REGISTRY,
    AgentExecutor,
    AgentNode,
    NODE_MAP,
    events_node,
    faq_node,
    tracking_node,
)
from services.central.policy import SentinelPolicy
from services.central.state import make_state


def test_tracking_node_result() -> None:
    state = make_state("where is vessel IMO-001")
    result = tracking_node(state)
    assert result["agent_result"] == {"lat": 0.0, "lon": 0.0, "vessel": "stub"}
    assert result["error"] is None


def test_tracking_node_audit_log() -> None:
    state = make_state("where is vessel IMO-001")
    result = tracking_node(state)
    assert len(result["audit_log"]) == 1
    assert result["audit_log"][0]["type"] == "tool_call"


def test_events_node_result() -> None:
    state = make_state("show me recent alerts")
    result = events_node(state)
    assert result["agent_result"] == [{"event": "stub", "severity": "low"}]
    assert result["error"] is None


def test_faq_node_result() -> None:
    state = make_state("what is the procedure for boarding")
    result = faq_node(state)
    assert result["agent_result"] == {"answer": "stub SOP response"}
    assert result["error"] is None


def test_cross_agent_policy_rejection() -> None:
    from services.central.agents import DEFAULT_POLICY_MAP
    policy = SentinelPolicy(DEFAULT_POLICY_MAP)
    executor = AgentExecutor(AGENT_REGISTRY, policy)
    # tracking node attempting to call an events tool — policy must reject
    rogue_node = AgentNode(executor, "tracking", "query_events")
    state = make_state("test")
    result = rogue_node(state)
    assert result["error"] == "not authorised"
    assert result["agent_result"] is None
    assert len(result["audit_log"]) == 1


def test_node_map_covers_all_intents() -> None:
    assert set(NODE_MAP.keys()) == {"TRACKING", "EVENTS", "SOP"}
