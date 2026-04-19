# Validation — Phase 2: Sentinel Policy Layer

_Branch: `phase-2-sentinel-policy-layer` | Date: 2026-04-19_

---

## Automated

### Tests (pytest)

Run: `pytest services/central/tests/test_sentinel_policy.py -v`

Required assertions (one per test):
- Permit path returns `None`
- Unknown agent returns `PolicyRejection(reason="unknown agent")`
- Unauthorised tool returns `PolicyRejection(reason="not authorised")`
- Cross-agent tool access is blocked (faq cannot call tracking tool)
- Calling exactly `max_calls` times all return `None`
- The `max_calls + 1`th call returns `PolicyRejection(reason="rate limit exceeded")`
- After window expiry, calls are permitted again
- `PolicyRejection.timestamp` is timezone-aware (not naive)
- `dataclasses.asdict(rejection)` produces a plain dict with no non-serialisable values

All tests must pass with zero failures and zero skips.

### Type checking (mypy)

Run: `mypy services/central/policy/sentinel_policy.py --strict`

Required: zero errors, zero warnings.

---

## Manual

1. Open `sentinel_policy.py` — confirm:
   - No imports beyond stdlib (`dataclasses`, `datetime`, `collections`)
   - `check` performs checks in the documented order (unknown agent → not
     authorised → rate limit → permit)
   - Rate limit pruning removes entries older than `window_seconds`, not `>=`

2. Construct a policy in a Python REPL and call `check` for a permitted tool —
   confirm it returns `None` and the call is recorded in `_call_log`

3. Call `check` for a cross-agent tool — confirm rejection reason is
   `"not authorised"`, not `"unknown agent"` (the agent exists; the tool doesn't)

4. Confirm `dataclasses.asdict(PolicyRejection(...))` produces a dict where
   `timestamp` is a `datetime` object — callers serialising to JSON will need
   to convert it, but it must not already be a string at this layer

---

## Definition of done

- [ ] `services/central/policy/sentinel_policy.py` exists with `RateLimit`,
      `PolicyRejection`, and `SentinelPolicy`
- [ ] `SentinelPolicy.check` enforces the three-step order (unknown → unauthorised
      → rate limit)
- [ ] All three canonical reason strings match the spec exactly
- [ ] `PolicyRejection.timestamp` is always timezone-aware UTC
- [ ] All pytest assertions pass (9 tests)
- [ ] `mypy --strict` reports zero errors
- [ ] `specs/roadmap.md` Phase 2 items checked off
