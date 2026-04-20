import json
import logging
import os
import time
from typing import Any

from services.central.crew import SENTINEL_GRAPH
from services.central.state import make_state
from services.api.models import TaskResponse
from services.api.task_store import get_task, save_task, serialize_agent_result

__all__ = ["consume_one", "run_consumer"]

logger = logging.getLogger(__name__)


def consume_one(sqs_client: Any, queue_url: str) -> bool:
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20,
    )
    messages = response.get("Messages", [])
    if not messages:
        return False

    message = messages[0]
    receipt_handle: str = message["ReceiptHandle"]

    try:
        body = json.loads(message["Body"])
        task_id: str = body["task_id"]
        query: str = body["query"]
    except (json.JSONDecodeError, KeyError) as exc:
        logger.error("Malformed SQS message, discarding: %s", exc)
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        return True

    existing = get_task(task_id)
    if existing is not None and existing.status != "pending":
        logger.info("Duplicate task_id %s already completed, skipping", task_id)
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
        return True

    try:
        result_state = SENTINEL_GRAPH.invoke(make_state(query))
    except Exception as exc:
        logger.error("Graph invocation failed for task %s: %s", task_id, exc)
        return True  # do not delete — allow redelivery

    task = TaskResponse(
        task_id=task_id,
        status="completed",
        intent=result_state.get("intent"),
        agent_result=serialize_agent_result(result_state.get("agent_result")),
        error=result_state.get("error"),
    )
    # Persist before deleting from queue so a crash between the two operations
    # leaves the task readable and the message redeliverable.
    save_task(task_id, task)
    sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    return True


def run_consumer(sqs_client: Any, queue_url: str) -> None:
    logger.info("SQS consumer started on %s", queue_url)
    while True:
        try:
            consume_one(sqs_client, queue_url)
        except Exception as exc:
            logger.error("Consumer loop error: %s", exc)
            time.sleep(5)


if __name__ == "__main__":
    import boto3

    logging.basicConfig(level=logging.INFO)
    queue_url = os.environ["QUEUE_URL"]
    region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-1"))
    kwargs: dict = {"region_name": region}
    if endpoint_url := os.environ.get("AWS_ENDPOINT_URL"):
        kwargs["endpoint_url"] = endpoint_url
    sqs = boto3.client("sqs", **kwargs)
    logger.info("Starting consumer on %s", queue_url)
    run_consumer(sqs, queue_url)
