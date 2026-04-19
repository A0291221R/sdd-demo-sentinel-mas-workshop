import re

import pytest
from fastapi.testclient import TestClient

from services.api.main import app
from services.api.task_store import TASK_STORE

UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@pytest.fixture(autouse=True)
def clear_task_store() -> None:
    TASK_STORE.clear()


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_health_returns_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_post_query_tracking(client: TestClient) -> None:
    r = client.post("/query", json={"query": "where is vessel IMO-001"})
    assert r.status_code == 202
    body = r.json()
    assert body["intent"] == "TRACKING"
    assert body["agent_result"] is not None
    assert body["error"] is None


def test_post_query_events(client: TestClient) -> None:
    r = client.post("/query", json={"query": "show me recent alerts for zone 3"})
    assert r.status_code == 202
    assert r.json()["intent"] == "EVENTS"
    assert r.json()["agent_result"] is not None


def test_post_query_sop(client: TestClient) -> None:
    r = client.post("/query", json={"query": "what is the procedure for safe boarding"})
    assert r.status_code == 202
    assert r.json()["intent"] == "SOP"
    assert r.json()["agent_result"] is not None


def test_post_query_unknown(client: TestClient) -> None:
    r = client.post("/query", json={"query": "hello world"})
    assert r.status_code == 202
    body = r.json()
    assert body["error"] is not None
    assert body["intent"] is None


def test_get_result_found(client: TestClient) -> None:
    post = client.post("/query", json={"query": "where is vessel IMO-001"})
    task_id = post.json()["task_id"]
    get = client.get(f"/result/{task_id}")
    assert get.status_code == 200
    assert get.json()["task_id"] == task_id
    assert get.json()["intent"] == "TRACKING"


def test_get_result_not_found(client: TestClient) -> None:
    r = client.get("/result/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


def test_post_query_empty_string(client: TestClient) -> None:
    r = client.post("/query", json={"query": ""})
    assert r.status_code == 422


def test_post_query_whitespace_only(client: TestClient) -> None:
    r = client.post("/query", json={"query": "   "})
    assert r.status_code == 422


def test_task_id_is_uuid(client: TestClient) -> None:
    r = client.post("/query", json={"query": "where is vessel IMO-001"})
    assert UUID4_RE.match(r.json()["task_id"])
