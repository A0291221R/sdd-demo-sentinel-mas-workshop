# Validation — Phase 7: FastAPI Service

---

## Automated

### Endpoint tests (`services/api/tests/test_endpoints.py`)

| # | Test | Assertion |
|---|------|-----------|
| 1 | `test_health_returns_ok` | GET /health → 200, body `{"status": "ok"}` |
| 2 | `test_post_query_tracking` | POST /query vessel query → 202, `intent=="TRACKING"`, `agent_result` not None, `error` is None |
| 3 | `test_post_query_events` | POST /query alert query → 202, `intent=="EVENTS"`, `agent_result` not None |
| 4 | `test_post_query_sop` | POST /query procedure query → 202, `intent=="SOP"`, `agent_result` not None |
| 5 | `test_post_query_unknown` | POST /query unrecognised → 202, `error` not None, `intent` is None |
| 6 | `test_get_result_found` | POST then GET /result/{task_id} → 200, payload matches POST response |
| 7 | `test_get_result_not_found` | GET /result/bad-id → 404 |
| 8 | `test_post_query_empty_string` | POST /query `""` → 422 |
| 9 | `test_task_id_is_uuid` | POST /query → `task_id` matches UUID4 regex |

### Type check

```
mypy services/api/main.py services/api/models.py services/api/task_store.py --strict --explicit-package-bases
```

Must pass with zero errors.

---

## Manual

1. Install dependencies: `py -3.11 -m pip install fastapi httpx`
2. Run new tests: `py -3.11 -m pytest services/api/tests/ -v`
3. Confirm 9 tests pass.
4. Run full suite: `py -3.11 -m pytest services/central/tests/ services/api/tests/ -v`
5. Confirm 50 existing + 9 new = 59 tests pass with no regressions.
6. Start the server manually and confirm OpenAPI docs load:
   ```
   py -3.11 -m uvicorn services.api.main:app --reload
   ```
   Open `http://localhost:8000/docs` — verify all three endpoints appear.
7. Use the Swagger UI to POST a query and GET the result by task_id.

---

## Definition of done

- [ ] `services/api/main.py` with `app`, three endpoints
- [ ] `services/api/models.py` with `QueryRequest` and `TaskResponse`
- [ ] `services/api/task_store.py` with in-memory store
- [ ] `POST /query` invokes `SENTINEL_GRAPH` and returns `TaskResponse` (202)
- [ ] `GET /result/{task_id}` returns stored result (200) or 404
- [ ] `GET /health` returns `{"status": "ok"}` (200)
- [ ] Empty query returns 422 (Pydantic validation)
- [ ] All 9 endpoint tests pass
- [ ] Full suite (59 tests) passes with no regressions
- [ ] `mypy --strict` passes on all three `services/api/*.py` files
- [ ] Phase 7 roadmap items marked `[x]`
