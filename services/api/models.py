from __future__ import annotations

from pydantic import BaseModel, field_validator


class QueryRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def query_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("query must not be empty")
        if len(v) > 1000:
            raise ValueError("query must not exceed 1000 characters")
        return v


class TaskResponse(BaseModel):
    task_id: str
    status: str
    intent: str | None
    agent_result: str | None
    error: str | None
