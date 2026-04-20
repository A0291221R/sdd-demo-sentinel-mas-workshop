from __future__ import annotations

import json
import os
from typing import Any

import psycopg2  # type: ignore[import-untyped]

from .models import TaskResponse

__all__ = ["TASK_STORE", "TaskResponse", "serialize_agent_result", "save_task", "get_task", "init_db"]

# In-memory fallback used when no DB is configured (tests, local runs without Postgres).
TASK_STORE: dict[str, TaskResponse] = {}


def _conn() -> Any:
    if dsn := os.environ.get("DATABASE_URL"):
        return psycopg2.connect(dsn)
    host = os.environ.get("DB_HOST")
    if not host:
        raise RuntimeError("No database configured (DB_HOST / DATABASE_URL not set)")
    return psycopg2.connect(
        host=host,
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "sentinel_mas"),
        user=os.environ.get("DB_USER", "sentinel"),
        password=os.environ.get("DB_PASSWORD", "localdev"),
    )


def _db_available() -> bool:
    return bool(os.environ.get("DATABASE_URL") or os.environ.get("DB_HOST"))


def init_db() -> None:
    if not _db_available():
        return
    with _conn() as conn, conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                status  TEXT NOT NULL,
                intent  TEXT,
                agent_result TEXT,
                error   TEXT
            )
        """)


def serialize_agent_result(result: object | None) -> str | None:
    if result is None or isinstance(result, str):
        return result
    try:
        return json.dumps(result)
    except (TypeError, ValueError):
        return None


def save_task(task_id: str, result: TaskResponse) -> None:
    if _db_available():
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO tasks (task_id, status, intent, agent_result, error)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (task_id) DO UPDATE SET
                    status       = EXCLUDED.status,
                    intent       = EXCLUDED.intent,
                    agent_result = EXCLUDED.agent_result,
                    error        = EXCLUDED.error
                """,
                (task_id, result.status, result.intent, result.agent_result, result.error),
            )
    else:
        TASK_STORE[task_id] = result


def get_task(task_id: str) -> TaskResponse | None:
    if _db_available():
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT task_id, status, intent, agent_result, error FROM tasks WHERE task_id = %s",
                (task_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return TaskResponse(task_id=row[0], status=row[1], intent=row[2], agent_result=row[3], error=row[4])
    return TASK_STORE.get(task_id)
