# Plan — Phase 7: FastAPI Service

---

## Group 1 — Pydantic models (`services/api/models.py`)

1.1 Define `QueryRequest(BaseModel)` with `query: str` (non-empty, max 1000 chars validator)  
1.2 Define `TaskResponse(BaseModel)` with `task_id`, `status`, `intent`, `agent_result`, `error` fields  
1.3 Confirm mypy strict passes on `models.py` in isolation  

---

## Group 2 — In-memory task store (`services/api/task_store.py`)

2.1 Define `TaskResult` as a `TypedDict` (or dataclass) mirroring `TaskResponse` fields  
2.2 Implement `TASK_STORE: dict[str, TaskResult]` module-level store  
2.3 Implement `save_task(task_id: str, result: TaskResult) -> None`  
2.4 Implement `get_task(task_id: str) -> TaskResult | None`  

---

## Group 3 — FastAPI app (`services/api/main.py`)

3.1 Create `app = FastAPI(title="Sentinel MAS API")`  
3.2 Implement `GET /health` → `{"status": "ok"}`  
3.3 Implement `POST /query`:  
  - Generate `task_id = str(uuid.uuid4())`  
  - Call `make_state(request.query)` then `SENTINEL_GRAPH.invoke(state)`  
  - Build `TaskResult` from the returned `GraphState`  
  - Call `save_task(task_id, result)`  
  - Return `TaskResponse` with `status="completed"`, HTTP 202  
3.4 Implement `GET /result/{task_id}`:  
  - Call `get_task(task_id)`  
  - Return `TaskResponse` if found, else `HTTPException(404)`  
3.5 Confirm mypy strict passes on `main.py`  

---

## Group 4 — Package wiring

4.1 Create `services/api/__init__.py` (empty)  
4.2 Create `services/api/tests/__init__.py` (empty)  
4.3 Verify `from services.api.main import app` works from repo root with `py -3.11`  

---

## Group 5 — Tests (`services/api/tests/test_endpoints.py`)

5.1 Fixture: `client` — `TestClient(app)` scoped to module  
5.2 `test_health_returns_ok` — GET /health → 200, `{"status": "ok"}`  
5.3 `test_post_query_tracking` — POST /query with vessel query → 202, `intent=="TRACKING"`, `agent_result` not None, `error` is None  
5.4 `test_post_query_events` — POST /query with alert query → 202, `intent=="EVENTS"`  
5.5 `test_post_query_sop` — POST /query with procedure query → 202, `intent=="SOP"`  
5.6 `test_post_query_unknown` — POST /query with unrecognised query → 202, `error` not None, `intent` is None  
5.7 `test_get_result_found` — POST /query then GET /result/{task_id} → 200, same payload  
5.8 `test_get_result_not_found` — GET /result/nonexistent-id → 404  
5.9 `test_post_query_empty_string` — POST /query with `""` → 422 (Pydantic validation error)  
5.10 Run full test suite; confirm 50 existing + 9 new = 59 tests pass  
