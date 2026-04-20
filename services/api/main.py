import json
import os
import uuid
from typing import Any

import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import QueryRequest, TaskResponse
from .settings import settings
from .task_store import get_task, init_db, save_task

__all__ = ["app"]

app = FastAPI(title="Sentinel MAS API")

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_sqs_client: Any = None


def _get_sqs_client() -> Any:
    global _sqs_client
    if _sqs_client is None:
        kwargs = {}
        if endpoint := os.environ.get("AWS_ENDPOINT_URL"):
            kwargs["endpoint_url"] = endpoint
        _sqs_client = boto3.client("sqs", **kwargs)
    return _sqs_client


def set_sqs_client(client: Any) -> None:
    global _sqs_client
    _sqs_client = client


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", status_code=202, response_model=TaskResponse)
def post_query(request: QueryRequest) -> TaskResponse:
    task_id = str(uuid.uuid4())
    try:
        _get_sqs_client().send_message(
            QueueUrl=settings.queue_url,
            MessageBody=json.dumps({"task_id": task_id, "query": request.query}),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Queue unavailable: {exc}") from exc
    task = TaskResponse(
        task_id=task_id,
        status="pending",
        intent=None,
        agent_result=None,
        error=None,
    )
    save_task(task_id, task)
    return task


@app.get("/result/{task_id}", response_model=TaskResponse)
def get_result(task_id: str) -> TaskResponse:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
