from __future__ import annotations

import dataclasses
import time

from services.central.policy import PolicyRejection, RateLimit, SentinelPolicy

POLICY_MAP: dict[str, set[str]] = {
    "tracking": {"get_position"},
    "events": {"query_events"},
    "faq": {"search_sop"},
}


def make_policy(rate_limits: dict[str, dict[str, RateLimit]] | None = None) -> SentinelPolicy:
    return SentinelPolicy(policy_map=POLICY_MAP, rate_limits=rate_limits)


def test_permit_returns_none() -> None:
    policy = make_policy()
    assert policy.check("tracking", "get_position") is None


def test_unknown_agent_rejected() -> None:
    policy = make_policy()
    rejection = policy.check("unknown_agent", "get_position")
    assert isinstance(rejection, PolicyRejection)
    assert rejection.reason == "unknown agent"
    assert rejection.agent == "unknown_agent"
    assert rejection.tool == "get_position"


def test_unauthorised_tool_rejected() -> None:
    policy = make_policy()
    rejection = policy.check("tracking", "query_events")
    assert isinstance(rejection, PolicyRejection)
    assert rejection.reason == "not authorised"


def test_cross_agent_access_blocked() -> None:
    policy = make_policy()
    rejection = policy.check("faq", "get_position")
    assert isinstance(rejection, PolicyRejection)
    assert rejection.reason == "not authorised"


def test_rate_limit_under_threshold_permits() -> None:
    policy = make_policy({"tracking": {"get_position": RateLimit(max_calls=3, window_seconds=60)}})
    for _ in range(3):
        assert policy.check("tracking", "get_position") is None


def test_rate_limit_exceeded_on_next_call() -> None:
    policy = make_policy({"tracking": {"get_position": RateLimit(max_calls=3, window_seconds=60)}})
    for _ in range(3):
        policy.check("tracking", "get_position")
    rejection = policy.check("tracking", "get_position")
    assert isinstance(rejection, PolicyRejection)
    assert rejection.reason == "rate limit exceeded"


def test_rate_limit_resets_after_window() -> None:
    policy = make_policy({"tracking": {"get_position": RateLimit(max_calls=2, window_seconds=1)}})
    for _ in range(2):
        policy.check("tracking", "get_position")

    blocked = policy.check("tracking", "get_position")
    assert isinstance(blocked, PolicyRejection)
    assert blocked.reason == "rate limit exceeded"

    time.sleep(1.05)
    assert policy.check("tracking", "get_position") is None


def test_policy_map_mutation_after_construction_has_no_effect() -> None:
    original_map: dict[str, set[str]] = {"tracking": {"get_position"}}
    policy = SentinelPolicy(policy_map=original_map)
    original_map["tracking"].add("query_events")  # mutate after construction
    rejection = policy.check("tracking", "query_events")
    assert isinstance(rejection, PolicyRejection)
    assert rejection.reason == "not authorised"


def test_rejection_timestamp_is_timezone_aware() -> None:
    policy = make_policy()
    rejection = policy.check("unknown_agent", "any_tool")
    assert rejection is not None
    assert rejection.timestamp.tzinfo is not None


def test_rate_limit_rejection_timestamp_is_timezone_aware() -> None:
    policy = make_policy({"tracking": {"get_position": RateLimit(max_calls=1, window_seconds=60)}})
    policy.check("tracking", "get_position")
    rejection = policy.check("tracking", "get_position")
    assert isinstance(rejection, PolicyRejection)
    assert rejection.timestamp.tzinfo is not None


def test_policy_rejection_is_dict_serialisable() -> None:
    policy = make_policy()
    rejection = policy.check("faq", "get_position")
    assert rejection is not None
    as_dict = dataclasses.asdict(rejection)
    assert isinstance(as_dict, dict)
    assert as_dict["agent"] == "faq"
    assert as_dict["tool"] == "get_position"
    assert as_dict["reason"] == "not authorised"
    assert "timestamp" in as_dict
