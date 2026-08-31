"""PostgreSQL에 사용자별 대화 이력을 영구 저장합니다."""

from uuid import uuid4

from app.memory.postgres_store import connect
from app.schemas import ConversationMessage


def append(user_id: str, session_id: str, role: str, content: str) -> ConversationMessage:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO conversation_messages (id, user_id, session_id, role, content) VALUES (%s, %s, %s, %s, %s)",
            (uuid4(), user_id, session_id, role, content),
        )
    return ConversationMessage(role=role, content=content)


def recent(user_id: str, session_id: str, limit: int = 10) -> list[ConversationMessage]:
    # 두 식별자를 모두 조건에 넣어 다른 사용자의 대화를 노출하지 않습니다.
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT role, content FROM (
                SELECT role, content, created_at
                FROM conversation_messages
                WHERE user_id = %s AND session_id = %s
                ORDER BY created_at DESC LIMIT %s
            ) recent_messages ORDER BY created_at
            """,
            (user_id, session_id, limit),
        )
        return [ConversationMessage(role=row[0], content=row[1]) for row in cursor.fetchall()]


def delete_for_user(user_id: str) -> int:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM conversation_messages WHERE user_id = %s", (user_id,))
        return cursor.rowcount
