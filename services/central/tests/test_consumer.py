import json
from unittest.mock import MagicMock, patch

import pytest

from services.central.consumer import consume_one
from services.api.task_store import TASK_STORE, TaskResponse


def _make_sqs_response(task_id: str, query: str) -> dict:
    return {
        "Messages": [
            {
                "Body": json.dumps({"task_id": task_id, "query": query}),
                "ReceiptHandle": "handle-abc",
            }
        ]
    }


def _empty_sqs_response() -> dict:
    return {"Messages": []}


@pytest.fixture(autouse=True)
def clear_store() -> None:
    TASK_STORE.clear()


def test_consume_one_no_messages() -> None:
    sqs = MagicMock()
    sqs.receive_message.return_value = _empty_sqs_response()
    result = consume_one(sqs, "https://sqs.test/queue")
    assert result is False
    sqs.delete_message.assert_not_called()
    assert len(TASK_STORE) == 0


def test_consume_one_tracking_message() -> None:
    sqs = MagicMock()
    sqs.receive_message.return_value = _make_sqs_response(
        "task-001", "where is vessel IMO-001"
    )
    result = consume_one(sqs, "https://sqs.test/queue")
    assert result is True
    assert "task-001" in TASK_STORE
    assert TASK_STORE["task-001"].intent == "TRACKING"
    assert TASK_STORE["task-001"].status == "completed"
    assert TASK_STORE["task-001"].agent_result is not None
    sqs.delete_message.assert_called_once()


def test_consume_one_events_message() -> None:
    sqs = MagicMock()
    sqs.receive_message.return_value = _make_sqs_response(
        "task-002", "show me recent alerts for zone 3"
    )
    consume_one(sqs, "https://sqs.test/queue")
    assert TASK_STORE["task-002"].intent == "EVENTS"


def test_consume_one_sop_message() -> None:
    sqs = MagicMock()
    sqs.receive_message.return_value = _make_sqs_response(
        "task-003", "what is the procedure for safe boarding"
    )
    consume_one(sqs, "https://sqs.test/queue")
    assert TASK_STORE["task-003"].intent == "SOP"


def test_consume_one_pending_task_is_reprocessed() -> None:
    """A task still in 'pending' state must be reprocessed (graph failure redelivery path)."""
    existing = TaskResponse(
        task_id="task-retry",
        status="pending",
        intent=None,
        agent_result=None,
        error=None,
    )
    TASK_STORE["task-retry"] = existing

    sqs = MagicMock()
    sqs.receive_message.return_value = _make_sqs_response(
        "task-retry", "where is vessel IMO-001"
    )
    result = consume_one(sqs, "https://sqs.test/queue")

    assert result is True
    assert TASK_STORE["task-retry"].status == "completed"
    assert TASK_STORE["task-retry"].intent == "TRACKING"
    sqs.delete_message.assert_called_once()


def test_consume_one_idempotency() -> None:
    existing = TaskResponse(
        task_id="task-dup",
        status="completed",
        intent="TRACKING",
        agent_result="cached",
        error=None,
    )
    TASK_STORE["task-dup"] = existing

    sqs = MagicMock()
    sqs.receive_message.return_value = _make_sqs_response(
        "task-dup", "where is vessel IMO-001"
    )
    with patch("services.central.consumer.SENTINEL_GRAPH") as mock_graph:
        result = consume_one(sqs, "https://sqs.test/queue")

    assert result is True
    mock_graph.invoke.assert_not_called()
    sqs.delete_message.assert_called_once()
    assert TASK_STORE["task-dup"].agent_result == "cached"


def test_consume_one_malformed_json() -> None:
    sqs = MagicMock()
    sqs.receive_message.return_value = {
        "Messages": [{"Body": "not-json", "ReceiptHandle": "handle-bad"}]
    }
    result = consume_one(sqs, "https://sqs.test/queue")
    assert result is True
    assert len(TASK_STORE) == 0
    sqs.delete_message.assert_called_once()


def test_consume_one_missing_fields() -> None:
    sqs = MagicMock()
    sqs.receive_message.return_value = {
        "Messages": [
            {"Body": json.dumps({"task_id": "task-x"}), "ReceiptHandle": "handle-mf"}
        ]
    }
    result = consume_one(sqs, "https://sqs.test/queue")
    assert result is True
    assert "task-x" not in TASK_STORE
    sqs.delete_message.assert_called_once()


def test_consume_one_graph_exception() -> None:
    sqs = MagicMock()
    sqs.receive_message.return_value = _make_sqs_response(
        "task-err", "where is vessel IMO-001"
    )
    with patch(
        "services.central.consumer.SENTINEL_GRAPH"
    ) as mock_graph:
        mock_graph.invoke.side_effect = RuntimeError("graph exploded")
        result = consume_one(sqs, "https://sqs.test/queue")

    assert result is True
    assert "task-err" not in TASK_STORE
    sqs.delete_message.assert_not_called()
