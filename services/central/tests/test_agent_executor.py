import pytest
from services.central.agents import AGENT_REGISTRY, DEFAULT_POLICY_MAP, AgentExecutor
from services.central.policy import SentinelPolicy
from services.central.state import make_state


@pytest.fixture
def executor() -> AgentExecutor:
    policy = SentinelPolicy(policy_map=DEFAULT_POLICY_MAP)
    return AgentExecutor(registry=AGENT_REGISTRY, policy=policy)


def test_tracking_permit(executor: AgentExecutor) -> None:
    state = make_state("where is vessel IMO 1234567?")
    result = executor.execute("tracking", "get_position", state)
    assert result["agent_result"] == {"lat": 0.0, "lon": 0.0, "vessel": "stub"}
    assert len(result["audit_log"]) == 1
    assert result["audit_log"][0] == {"type": "tool_call", "agent": "tracking", "tool": "get_position"}


def test_events_permit(executor: AgentExecutor) -> None:
    state = make_state("show recent alerts")
    result = executor.execute("events", "query_events", state)
    assert result["agent_result"] == [{"event": "stub", "severity": "low"}]
    assert len(result["audit_log"]) == 1
    assert result["audit_log"][0]["type"] == "tool_call"


def test_faq_permit(executor: AgentExecutor) -> None:
    state = make_state("what is the boarding procedure?")
    result = executor.execute("faq", "search_sop", state)
    assert result["agent_result"] == {"answer": "stub SOP response"}
    assert len(result["audit_log"]) == 1
    assert result["audit_log"][0]["type"] == "tool_call"


def test_cross_agent_rejection_does_not_overwrite_agent_result(executor: AgentExecutor) -> None:
    state = make_state("test")
    state["agent_result"] = "sentinel"  # proves rejection path never touches agent_result
    result = executor.execute("faq", "get_position", state)
    assert result["error"] == "not authorised"
    assert result["agent_result"] == "sentinel"
    assert len(result["audit_log"]) == 1
    assert result["audit_log"][0]["reason"] == "not authorised"


def test_unknown_agent_raises_key_error(executor: AgentExecutor) -> None:
    state = make_state("test")
    with pytest.raises(KeyError):
        executor.execute("ghost", "get_position", state)


def test_unauthorised_tool_returns_rejection(executor: AgentExecutor) -> None:
    # Policy rejects before tool lookup — "not authorised" is the expected outcome
    # for a tool not in the policy map (not a KeyError).
    state = make_state("test")
    result = executor.execute("tracking", "nonexistent", state)
    assert result["error"] == "not authorised"
    assert len(result["audit_log"]) == 1


def test_tool_exception_logs_error_and_does_not_set_agent_result(executor: AgentExecutor) -> None:
    from services.central.agents.crew_agents import AgentRuntime
    from types import MappingProxyType

    def _failing_tool(**kwargs: object) -> object:
        raise RuntimeError("upstream unavailable")

    registry: dict[str, AgentRuntime] = {
        "tracking": AgentRuntime(
            llm_model="gpt-4o-mini",
            llm_temperature=0.0,
            system_prompt="stub",
            tools={"get_position": _failing_tool},
        )
    }
    policy = SentinelPolicy(policy_map={"tracking": {"get_position"}})
    ex = AgentExecutor(registry=registry, policy=policy)
    state = make_state("test")
    result = ex.execute("tracking", "get_position", state)
    assert result["error"] == "upstream unavailable"
    assert result["agent_result"] is None
    assert len(result["audit_log"]) == 1
    assert result["audit_log"][0]["type"] == "tool_error"
    assert result["audit_log"][0]["error"] == "upstream unavailable"


def test_audit_log_accumulates_across_calls(executor: AgentExecutor) -> None:
    state = make_state("test")
    executor.execute("tracking", "get_position", state)
    executor.execute("events", "query_events", state)
    assert len(state["audit_log"]) == 2
