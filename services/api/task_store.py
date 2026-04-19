import json

from .models import TaskResponse

__all__ = ["TASK_STORE", "serialize_agent_result", "save_task", "get_task"]

TASK_STORE: dict[str, TaskResponse] = {}


def serialize_agent_result(result: object | None) -> str | None:
    if result is None or isinstance(result, str):
        return result
    try:
        return json.dumps(result)
    except (TypeError, ValueError):
        return None


def save_task(task_id: str, result: TaskResponse) -> None:
    TASK_STORE[task_id] = result


def get_task(task_id: str) -> TaskResponse | None:
    return TASK_STORE.get(task_id)
