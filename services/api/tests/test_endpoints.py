import re
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from services.api.main import app, set_sqs_client
from services.api.task_store import TASK_STORE
from services.central.consumer import consume_one

UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


@pytest.fixture(autouse=True)
def clear_task_store() -> None:
    TASK_STORE.clear()


@pytest.fixture(autouse=True)
def mock_sqs(mock_sqs_client: MagicMock) -> None:
    set_sqs_client(mock_sqs_client)


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_sqs_client() -> MagicMock:
    return MagicMock()


def test_health_returns_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_post_query_returns_pending(client: TestClient, mock_sqs_client: MagicMock) -> None:
    r = client.post("/query", json={"query": "where is vessel IMO-001"})
    assert r.status_code == 202
    body = r.json()
    assert body["status"] == "pending"
    assert body["intent"] is None
    assert body["agent_result"] is None
    assert body["error"] is None
    mock_sqs_client.send_message.assert_called_once()


def test_post_query_tracking(client: TestClient, mock_sqs_client: MagicMock) -> None:
    r = client.post("/query", json={"query": "where is vessel IMO-001"})
    assert r.status_code == 202
    assert r.json()["status"] == "pending"


def test_post_query_events(client: TestClient, mock_sqs_client: MagicMock) -> None:
    r = client.post("/query", json={"query": "show me recent alerts for zone 3"})
    assert r.status_code == 202
    assert r.json()["status"] == "pending"


def test_post_query_sop(client: TestClient, mock_sqs_client: MagicMock) -> None:
    r = client.post("/query", json={"query": "what is the procedure for safe boarding"})
    assert r.status_code == 202
    assert r.json()["status"] == "pending"


def test_post_query_unknown(client: TestClient, mock_sqs_client: MagicMock) -> None:
    r = client.post("/query", json={"query": "hello world"})
    assert r.status_code == 202
    assert r.json()["status"] == "pending"


def test_get_result_pending_then_completed(
    client: TestClient, mock_sqs_client: MagicMock
) -> None:
    post = client.post("/query", json={"query": "where is vessel IMO-001"})
    task_id = post.json()["task_id"]

    # before consumer runs: pending
    get_pending = client.get(f"/result/{task_id}")
    assert get_pending.json()["status"] == "pending"

    # simulate consumer processing the enqueued message
    import json as _json
    call_args = mock_sqs_client.send_message.call_args
    body = _json.loads(call_args.kwargs["MessageBody"])
    sqs_stub = MagicMock()
    sqs_stub.receive_message.return_value = {
        "Messages": [{"Body": _json.dumps(body), "ReceiptHandle": "r"}]
    }
    consume_one(sqs_stub, "https://sqs.test/queue")

    # after consumer runs: completed
    get_done = client.get(f"/result/{task_id}")
    assert get_done.status_code == 200
    assert get_done.json()["status"] == "completed"
    assert get_done.json()["intent"] == "TRACKING"


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


def test_task_id_is_uuid(client: TestClient, mock_sqs_client: MagicMock) -> None:
    r = client.post("/query", json={"query": "where is vessel IMO-001"})
    assert UUID4_RE.match(r.json()["task_id"])
