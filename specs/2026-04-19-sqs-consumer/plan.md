# Plan — Phase 8: SQS Consumer

---

## Group 1 — Settings (`services/api/settings.py`)

1.1 Create `Settings(BaseSettings)` with `queue_url: str` field  
1.2 Default `queue_url` to `""` (overridden by env var `QUEUE_URL` at runtime)  
1.3 Expose module-level `settings = Settings()` instance  
1.4 Confirm mypy strict passes on `settings.py`  

---

## Group 2 — Consumer (`services/central/consumer.py`)

2.1 Import `SENTINEL_GRAPH`, `make_state` from `services.central`  
2.2 Import `save_task`, `serialize_agent_result`, `TASK_STORE` from `services.api.task_store`  
2.3 Import `TaskResponse` from `services.api.models`  
2.4 Implement `consume_one(sqs_client, queue_url) -> bool`:  
  - `receive_message` with `WaitTimeSeconds=20`, `MaxNumberOfMessages=1`  
  - Return `False` if no messages  
  - Parse JSON body; on parse error → log, delete, return `True`  
  - Idempotency check: if `task_id` in `TASK_STORE` → delete, return `True`  
  - Invoke graph, save `TaskResponse`, delete message, return `True`  
  - On graph exception → log, do NOT delete (allow redelivery)  
2.5 Implement `run_consumer(sqs_client, queue_url) -> None`:  
  - Infinite loop calling `consume_one()`  
  - Catch and log all exceptions; sleep 5 s on boto3 receive error  
2.6 Confirm mypy strict passes on `consumer.py`  

---

## Group 3 — Update `POST /query` (`services/api/main.py`)

3.1 Import `settings` from `.settings` and `json`  
3.2 Create module-level `sqs_client` (boto3 SQS client) — lazy init, injectable for tests  
3.3 Update `post_query` to call `sqs_client.send_message()` instead of invoking graph  
3.4 Return `TaskResponse(task_id=..., status="pending", intent=None, agent_result=None, error=None)`  
3.5 Save the pending task to `TASK_STORE` immediately so `GET /result` returns `status: "pending"`  
3.6 Confirm mypy strict still passes on `main.py`  

---

## Group 4 — Tests (`services/central/tests/test_consumer.py`)

4.1 Fixture: `mock_sqs` — `MagicMock` with canned `receive_message` response  
4.2 `test_consume_one_no_messages` — empty receive → returns `False`, no graph call  
4.3 `test_consume_one_tracking_message` — valid TRACKING query → returns `True`, `TASK_STORE` updated, message deleted  
4.4 `test_consume_one_events_message` — valid EVENTS query → `TASK_STORE["task_id"].intent == "EVENTS"`  
4.5 `test_consume_one_idempotency` — pre-populate `TASK_STORE` with task_id → message deleted, graph NOT called  
4.6 `test_consume_one_malformed_json` — body is not JSON → message deleted, `TASK_STORE` unchanged  
4.7 `test_consume_one_missing_fields` — body missing `query` key → message deleted, `TASK_STORE` unchanged  
4.8 `test_consume_one_graph_exception` — graph raises → message NOT deleted, `TASK_STORE` unchanged  

---

## Group 5 — Update endpoint tests (`services/api/tests/test_endpoints.py`)

5.1 Update `test_post_query_tracking` — response `status == "pending"`, `intent is None`, `agent_result is None`  
5.2 Update `test_post_query_events` — same pattern  
5.3 Update `test_post_query_sop` — same pattern  
5.4 Update `test_post_query_unknown` — `status == "pending"`, no error in POST response  
5.5 Update `test_get_result_found` — stub consumer call to populate store, then verify GET  
5.6 Keep `test_health_returns_ok`, `test_get_result_not_found`, `test_post_query_empty_string`, `test_post_query_whitespace_only`, `test_task_id_is_uuid` unchanged  

---

## Group 6 — Full suite verification

6.1 Run `py -3.11 -m pytest services/central/tests/ services/api/tests/ -v`  
6.2 Confirm 60 existing + 8 new consumer tests = 68 tests pass  
6.3 Run mypy strict on `consumer.py`, `settings.py`, updated `main.py`  
