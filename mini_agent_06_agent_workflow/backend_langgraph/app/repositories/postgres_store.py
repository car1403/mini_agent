import json
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb


class PostgresStore:
    """장기 Memory와 Agent 실행 이력을 PostgreSQL에 저장합니다."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self):
        return psycopg.connect(self.database_url)

    def add_memory(self, user_id: str, key: str, value: str) -> dict:
        memory_id = uuid4()
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO user_memories (id, user_id, memory_key, memory_value)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id, memory_key)
                DO UPDATE SET memory_value = EXCLUDED.memory_value, updated_at = NOW()
                RETURNING id, user_id, memory_key, memory_value
                """,
                (memory_id, user_id, key, value),
            )
            row = cursor.fetchone()
        return {"id": str(row[0]), "user_id": row[1], "key": row[2], "value": row[3]}

    def list_memories(self, user_id: str) -> list[dict]:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, memory_key, memory_value
                FROM user_memories WHERE user_id = %s ORDER BY created_at
                """,
                (user_id,),
            )
            rows = cursor.fetchall()
        return [
            {"id": str(row[0]), "user_id": row[1], "key": row[2], "value": row[3]}
            for row in rows
        ]

    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_memories WHERE user_id = %s AND id = %s",
                (user_id, memory_id),
            )
            return cursor.rowcount == 1

    def create_run(self, data: dict) -> dict:
        run_id = uuid4()
        request = data.get("request", {})
        result = data.get("result")
        trace = data.get("trace", [])
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agent_runs
                    (id, user_id, provider, model, status, request, result, trace)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    run_id,
                    data["user_id"],
                    data.get("provider", "mock"),
                    data.get("model", "deterministic-travel-mock"),
                    data["status"],
                    Jsonb(request),
                    Jsonb(result) if result is not None else None,
                    Jsonb(trace),
                ),
            )
        return {"run_id": str(run_id), **data}

    def get_run(self, run_id: str) -> dict | None:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, user_id, provider, model, status, request, result, trace
                FROM agent_runs WHERE id = %s
                """,
                (run_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return {
            "run_id": str(row[0]),
            "user_id": row[1],
            "provider": row[2],
            "model": row[3],
            "status": row[4],
            "request": row[5],
            "result": row[6],
            "trace": row[7],
            "current_node": row[4],
            "message": "",
            "requires_approval": row[4] == "waiting_approval",
        }

    def update_run(self, run_id: str, updates: dict) -> dict | None:
        current = self.get_run(run_id)
        if current is None:
            return None
        merged = {**current, **updates}
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE agent_runs
                SET status = %s, result = %s, trace = %s, updated_at = NOW()
                WHERE id = %s
                """,
                (
                    merged["status"],
                    Jsonb(merged.get("result")),
                    Jsonb(merged.get("trace", [])),
                    run_id,
                ),
            )
        return merged
