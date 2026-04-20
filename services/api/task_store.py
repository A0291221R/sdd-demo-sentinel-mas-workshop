import json
import os

import psycopg2

from .models import TaskResponse

__all__ = ["serialize_agent_result", "save_task", "get_task", "init_db"]


def _conn():
    if dsn := os.environ.get("DATABASE_URL"):
        return psycopg2.connect(dsn)
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "sentinel_mas"),
        user=os.environ.get("DB_USER", "sentinel"),
        password=os.environ.get("DB_PASSWORD", "localdev"),
    )


def init_db() -> None:
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


def get_task(task_id: str) -> TaskResponse | None:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT task_id, status, intent, agent_result, error FROM tasks WHERE task_id = %s",
            (task_id,),
        )
        row = cur.fetchone()
    if row is None:
        return None
    return TaskResponse(task_id=row[0], status=row[1], intent=row[2], agent_result=row[3], error=row[4])
