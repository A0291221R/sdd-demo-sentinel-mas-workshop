# Requirements — Phase 7: FastAPI Service

_Branch: `phase-7-fastapi-service` | Date: 2026-04-19_

---

## Scope

### Included

Implement a FastAPI application in `services/api/` with three endpoints:

- `POST /query` — accepts a natural language query, invokes `SENTINEL_GRAPH`
  synchronously, stores the result in an in-memory task store, returns a
  `task_id` (UUID) and `status`.
- `GET /result/{task_id}` — reads the stored `GraphState` result and returns
  a structured response; returns 404 if task ID is unknown.
- `GET /health` — returns `{"status": "ok"}` for liveness checks.

Auto-generate OpenAPI docs via FastAPI default (`/docs`, `/redoc`).

Write pytest endpoint tests using FastAPI's `TestClient` (httpx).

### Not included

- No real SQS enqueue — Phase 8 wires the SQS consumer. `POST /query` calls
  `SENTINEL_GRAPH.invoke()` directly and is synchronous in this phase.
- No RDS persistence — task results are stored in a process-level `dict`.
  Phase 8 replaces this with a real audit log write.
- No authentication / API keys on endpoints — out of scope for this phase.
- No docker compose changes — Phase 10 handles infrastructure.

---

## API contract

### `POST /query`

**Request body:**
```json
{ "query": "where is vessel IMO-001" }
```

**Response `202`:**
```json
{
  "task_id": "<uuid4>",
  "status": "completed",
  "intent": "TRACKING",
  "agent_result": "Vessel IMO-001 is at ...",
  "error": null
}
```

If the router could not classify the query, `intent` is `null`, `agent_result`
is `null`, and `error` is a non-empty string. HTTP status is still `200`/`202`
— classification failure is a domain outcome, not an HTTP error.

### `GET /result/{task_id}`

**Response `200`:**
```json
{
  "task_id": "<uuid4>",
  "status": "completed",
  "intent": "TRACKING",
  "agent_result": "...",
  "error": null
}
```

**Response `404`:** `{ "detail": "Task not found" }` when task ID is unknown.

### `GET /health`

**Response `200`:** `{ "status": "ok" }`

---

## Data shapes

### Request model

| Field | Type | Validation |
|-------|------|------------|
| `query` | `str` | Non-empty, max 1000 chars |

### Response model

| Field | Type | Notes |
|-------|------|-------|
| `task_id` | `str` | UUID4 string |
| `status` | `str` | Always `"completed"` in this phase |
| `intent` | `str \| None` | One of `TRACKING`, `EVENTS`, `SOP`, or `None` |
| `agent_result` | `str \| None` | Raw agent output string |
| `error` | `str \| None` | Error message or `None` |

---

## Decisions

**Synchronous graph invocation (no SQS)**
Phase 8 introduces the SQS consumer. Stubbing SQS here would add complexity
(LocalStack, boto3 mocking) with no test value. Calling `SENTINEL_GRAPH.invoke()`
directly keeps this phase independently testable and shippable.

**In-memory task store**
A `dict[str, TaskResult]` at module level is sufficient for this phase.
Phase 8 writes to RDS; Phase 7 just needs GET /result to work consistently
within a process. No persistence across restarts is required.

**202 vs 200 for POST /query**
Using `202 Accepted` signals that the request was received and processed
asynchronously in the production design. Even though this phase is synchronous,
using 202 now avoids a client-breaking status change when Phase 8 decouples.

**Pydantic models for request/response**
Consistent with the tech stack. FastAPI validates incoming bodies and
serialises responses automatically. No extra validation library needed.

**File location**
New service directory `services/api/` separate from `services/central/`.
The API service is a distinct deployment unit; it imports from `services.central`
but does not live inside it.

---

## Context

- File locations:
  - `services/api/main.py` — FastAPI `app` instance and endpoint definitions
  - `services/api/models.py` — Pydantic request/response models
  - `services/api/task_store.py` — in-memory `dict` store + `TaskResult` type
  - `services/api/tests/test_endpoints.py` — TestClient endpoint tests
- Import pattern:
  - `from services.central.crew import SENTINEL_GRAPH`
  - `from services.central.state import make_state`
- FastAPI and httpx must be installed: confirm in `py -3.11` environment before
  implementing (`pip install fastapi httpx`)
- Follow the same `py -3.11 -m pytest` invocation used in all prior phases
- mypy strict must pass on `services/api/main.py` and `services/api/models.py`
- No new dependencies beyond `fastapi`, `httpx`, and `pydantic` (already in
  tech stack; httpx is FastAPI's recommended test client)
