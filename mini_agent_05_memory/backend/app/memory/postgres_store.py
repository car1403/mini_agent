from uuid import uuid4

import psycopg

from app.config import settings
from app.memory.policy import validate_memory_key
from app.schemas import MemoryItem


def connect():
    return psycopg.connect(settings.database_url)


def upsert(user_id: str, key: str, value: str) -> MemoryItem:
    validate_memory_key(key)
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO user_memories (id, user_id, memory_key, memory_value)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, memory_key)
            DO UPDATE SET memory_value = EXCLUDED.memory_value, updated_at = NOW()
            RETURNING id, user_id, memory_key, memory_value
            """,
            (uuid4(), user_id, key, value),
        )
        row = cursor.fetchone()
    return MemoryItem(id=str(row[0]), user_id=row[1], key=row[2], value=row[3])


def list_for_user(user_id: str) -> list[MemoryItem]:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, user_id, memory_key, memory_value
            FROM user_memories WHERE user_id = %s ORDER BY created_at
            """,
            (user_id,),
        )
        return [
            MemoryItem(id=str(row[0]), user_id=row[1], key=row[2], value=row[3])
            for row in cursor.fetchall()
        ]


def delete(user_id: str, memory_id: str) -> bool:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM user_memories WHERE user_id = %s AND id = %s",
            (user_id, memory_id),
        )
        return cursor.rowcount == 1
