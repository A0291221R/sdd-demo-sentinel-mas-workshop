import pytest
from langgraph.graph.state import CompiledStateGraph

from services.central.crew import build_graph
from services.central.state import GraphState, make_state


@pytest.fixture
def graph() -> CompiledStateGraph[GraphState]:
    return build_graph()


def test_tracking_intent_end_to_end(graph: CompiledStateGraph[GraphState]) -> None:
    result = graph.invoke(make_state("where is vessel IMO-001"))
    assert result["intent"] == "TRACKING"
    assert result["agent_result"] is not None
    assert result["error"] is None
    assert len(result["audit_log"]) >= 1


def test_events_intent_end_to_end(graph: CompiledStateGraph[GraphState]) -> None:
    result = graph.invoke(make_state("show me recent alerts for zone 3"))
    assert result["intent"] == "EVENTS"
    assert result["agent_result"] is not None
    assert result["error"] is None


def test_sop_intent_end_to_end(graph: CompiledStateGraph[GraphState]) -> None:
    result = graph.invoke(make_state("what is the procedure for safe boarding"))
    assert result["intent"] == "SOP"
    assert result["agent_result"] is not None
    assert result["error"] is None


def test_unknown_query_sets_error(graph: CompiledStateGraph[GraphState]) -> None:
    result = graph.invoke(make_state("hello world"))
    assert result["error"] is not None
    assert result["intent"] is None
