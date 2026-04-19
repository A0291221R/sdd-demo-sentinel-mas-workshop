# Changelog

All notable changes to Sentinel MAS are documented here.
Entries are created automatically by `/feature-spec` and closed by `/changelog`.

## Unreleased

### phase-2-sentinel-policy-layer — 2026-04-19
- Branch: `phase-2-sentinel-policy-layer`
- Spec: `specs/2026-04-19-sentinel-policy-layer/`
- Status: merged
- Summary: Implements SentinelPolicy with frozen policy_map, per-agent/per-tool sliding-window rate limiting, threading.Lock on the prune/check/append sequence, and UTC-aware PolicyRejection. 11 tests, mypy strict clean.

### phase-1-shared-state-schema — 2026-04-19
- Branch: `phase-1-shared-state-schema`
- Spec: `specs/2026-04-19-shared-state-schema/`
- Status: merged
- Summary: Defined `GraphState` TypedDict with `operator.add` reducer on `audit_log`, `Literal` type for `intent`, and `make_state()` factory for safe initialisation. 10 tests, mypy strict clean.

<!-- feature entries will appear here -->
