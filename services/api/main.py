import uuid

from fastapi import FastAPI, HTTPException

from services.central.crew import SENTINEL_GRAPH
from services.central.state import make_state

from .models import QueryRequest, TaskResponse
from .task_store import get_task, save_task, serialize_agent_result

__all__ = ["app"]

app = FastAPI(title="Sentinel MAS API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", status_code=202, response_model=TaskResponse)
def post_query(request: QueryRequest) -> TaskResponse:
    task_id = str(uuid.uuid4())
    state = make_state(request.query)
    result_state = SENTINEL_GRAPH.invoke(state)

    task = TaskResponse(
        task_id=task_id,
        status="completed",
        intent=result_state.get("intent"),
        agent_result=serialize_agent_result(result_state.get("agent_result")),
        error=result_state.get("error"),
    )
    save_task(task_id, task)
    return task


@app.get("/result/{task_id}", response_model=TaskResponse)
def get_result(task_id: str) -> TaskResponse:
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
