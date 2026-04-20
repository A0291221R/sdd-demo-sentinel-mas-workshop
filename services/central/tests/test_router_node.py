from __future__ import annotations

from services.central.router import router_node
from services.central.state import make_state


def test_tracking_intent() -> None:
    state = make_state("where is vessel IMO-001")
    result = router_node(state)
    assert result["intent"] == "TRACKING"
    assert result["error"] is None


def test_events_intent() -> None:
    state = make_state("show me recent alerts for zone 3")
    result = router_node(state)
    assert result["intent"] == "EVENTS"
    assert result["error"] is None


def test_sop_intent() -> None:
    state = make_state("what is the procedure for onboarding a new operator")
    result = router_node(state)
    assert result["intent"] == "SOP"
    assert result["error"] is None


def test_unknown_intent_sets_error() -> None:
    state = make_state("hello world")
    result = router_node(state)
    assert result["intent"] is None
    assert result["error"] is not None
    assert "hello world" in result["error"]


def test_case_insensitive() -> None:
    state = make_state("TRACK the vessel heading north")
    result = router_node(state)
    assert result["intent"] == "TRACKING"


def test_first_match_tracking_over_events() -> None:
    state = make_state("track vessel alert status")
    result = router_node(state)
    assert result["intent"] == "TRACKING"


def test_runbook_maps_to_sop() -> None:
    state = make_state("show me the runbook for safe boarding procedures")
    result = router_node(state)
    assert result["intent"] == "SOP"


def test_lat_lon_maps_to_tracking() -> None:
    state = make_state("get lat lon for ship 42")
    result = router_node(state)
    assert result["intent"] == "TRACKING"
