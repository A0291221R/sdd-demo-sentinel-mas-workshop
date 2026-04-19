# Validation — Phase 8: SQS Consumer

---

## Automated

### Consumer unit tests (`services/central/tests/test_consumer.py`)

| # | Test | Assertion |
|---|------|-----------|
| 1 | `test_consume_one_no_messages` | Empty receive → returns `False`, `TASK_STORE` unchanged |
| 2 | `test_consume_one_tracking_message` | Valid query → returns `True`, `TASK_STORE[task_id].intent == "TRACKING"`, message deleted |
| 3 | `test_consume_one_events_message` | Valid query → `TASK_STORE[task_id].intent == "EVENTS"` |
| 4 | `test_consume_one_idempotency` | Pre-populated task_id → message deleted, graph not called |
| 5 | `test_consume_one_malformed_json` | Non-JSON body → message deleted, `TASK_STORE` unchanged |
| 6 | `test_consume_one_missing_fields` | Missing `query` key → message deleted, `TASK_STORE` unchanged |
| 7 | `test_consume_one_graph_exception` | Graph raises → message NOT deleted, `TASK_STORE` unchanged |
| 8 | `test_consume_one_sop_message` | Valid SOP query → `TASK_STORE[task_id].intent == "SOP"` |

### Updated endpoint tests

- `POST /query` now returns `status: "pending"`, `intent: null`, `agent_result: null`
- `GET /result/{task_id}` returns `"pending"` until consumer writes result

### Type check

```
mypy services/central/consumer.py services/api/settings.py services/api/main.py --strict --explicit-package-bases
```

Must pass with zero errors.

---

## Manual

1. Install dependencies: `py -3.11 -m pip install boto3 pydantic-settings`
2. Run consumer tests: `py -3.11 -m pytest services/central/tests/test_consumer.py -v`
3. Confirm 8 tests pass.
4. Run full suite: `py -3.11 -m pytest services/central/tests/ services/api/tests/ -v`
5. Confirm 68 tests pass with no regressions.
6. End-to-end smoke test (manual):
   - Start the API: `py -3.11 -m uvicorn services.api.main:app --reload`
   - POST a query: `curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query": "where is vessel IMO-001"}'`
   - Confirm response: `{"task_id": "...", "status": "pending", ...}`
   - Run one consumer cycle manually in Python:
     ```python
     import boto3, os
     from services.central.consumer import consume_one
     client = boto3.client("sqs", endpoint_url=os.getenv("SQS_ENDPOINT_URL"))
     consume_one(client, os.getenv("QUEUE_URL"))
     ```
   - GET the result: `curl http://localhost:8000/result/<task_id>`
   - Confirm `status: "completed"` and populated `intent`/`agent_result`

---

## Definition of done

- [ ] `services/central/consumer.py` with `consume_one` and `run_consumer`
- [ ] `services/api/settings.py` with `Settings(BaseSettings)` and `queue_url`
- [ ] `POST /query` enqueues to SQS (stubbed), returns `status: "pending"`
- [ ] Consumer idempotency: duplicate task_id skips re-processing
- [ ] Consumer poison pill: malformed messages deleted without crashing
- [ ] Consumer safety: graph exceptions do NOT delete the message
- [ ] All 8 consumer tests pass
- [ ] Full suite (68 tests) passes with no regressions
- [ ] `mypy --strict` passes on `consumer.py`, `settings.py`, `main.py`
- [ ] Phase 8 roadmap items marked `[x]`
