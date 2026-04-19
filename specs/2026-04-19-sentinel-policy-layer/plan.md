# Plan — Phase 2: Sentinel Policy Layer

_Branch: `phase-2-sentinel-policy-layer` | Date: 2026-04-19_

---

## Group 1 — Directory scaffold

1. Create `services/central/policy/` directory with `__init__.py`

## Group 2 — Data classes

2. Create `services/central/policy/sentinel_policy.py`
3. Import: `dataclass` from `dataclasses`; `datetime`, `timezone` from `datetime`;
   `deque` from `collections`; `defaultdict` from `collections`
4. Define `@dataclass RateLimit` with fields `max_calls: int` and `window_seconds: int`
5. Define `@dataclass PolicyRejection` with fields:
   - `agent: str`
   - `tool: str`
   - `reason: str`
   - `timestamp: datetime`

## Group 3 — `SentinelPolicy` class

6. Define `class SentinelPolicy` with `__init__(self, policy_map, rate_limits)`:
   - `policy_map: dict[str, set[str]]`
   - `rate_limits: dict[str, dict[str, RateLimit]]` (default empty dict)
   - Internal: `_call_log: defaultdict[str, defaultdict[str, deque[datetime]]]`
     initialised to `defaultdict(lambda: defaultdict(deque))`

7. Implement `check(self, agent: str, tool: str) -> PolicyRejection | None`:
   - Step 1 — unknown agent: if `agent not in self.policy_map`, return
     `PolicyRejection(agent, tool, "unknown agent", datetime.now(timezone.utc))`
   - Step 2 — not authorised: if `tool not in self.policy_map[agent]`, return
     `PolicyRejection(agent, tool, "not authorised", datetime.now(timezone.utc))`
   - Step 3 — rate limit: if a `RateLimit` exists for `(agent, tool)`:
     - Prune timestamps older than `window_seconds` from the deque
     - If `len(deque) >= max_calls`, return
       `PolicyRejection(agent, tool, "rate limit exceeded", datetime.now(timezone.utc))`
   - Step 4 — permit: append `datetime.now(timezone.utc)` to `_call_log[agent][tool]`;
     return `None`

## Group 4 — Exports

8. Export `SentinelPolicy`, `PolicyRejection`, `RateLimit` from
   `services/central/policy/__init__.py`

## Group 5 — Unit tests

9. Create `services/central/tests/test_sentinel_policy.py`

10. **Permit path**: construct a policy with one agent and one allowed tool;
    assert `check(agent, tool)` returns `None`

11. **Unknown agent**: assert `check("unknown_agent", "any_tool")` returns a
    `PolicyRejection` with `reason == "unknown agent"`

12. **Not authorised**: construct policy where tracking agent may not call
    `query_events`; assert `check("tracking", "query_events")` returns
    `PolicyRejection` with `reason == "not authorised"`

13. **Cross-agent access blocked**: assert faq agent cannot call tracking tool
    (verifies isolation between agents)

14. **Rate limit — under threshold**: call `check` `max_calls` times; assert all
    return `None`

15. **Rate limit — at threshold**: call `check` `max_calls + 1` times; assert the
    last call returns `PolicyRejection` with `reason == "rate limit exceeded"`

16. **Rate limit — window expiry**: call `check` `max_calls` times with a 1-second
    window; advance time past the window (monkeypatch `datetime.now` or use a
    very short window + `time.sleep(1)`); assert next call returns `None`

17. **`PolicyRejection` has UTC timestamp**: assert `rejection.timestamp.tzinfo` is
    not `None` (naive datetime is a bug)

18. **`dataclasses.asdict` serialisable**: assert `dataclasses.asdict(rejection)`
    produces a plain dict — confirms it can be appended to `GraphState.audit_log`
