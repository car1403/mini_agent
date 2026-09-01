r"""06. PostgreSQL에 사용자별 장기 Memory를 저장·조회·삭제합니다.

학습 목표:
- 장기 Memory가 프로세스 종료 후에도 PostgreSQL에 남는 이유를 이해합니다.
- upsert와 사용자 범위 조회·삭제를 직접 SQL로 확인합니다.

실행: python .\06_postgres_long_term_memory.py
외부 서비스: PostgreSQL과 user_memories 테이블 필요
"""

import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
import psycopg


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db")


def upsert_memory(user_id: str, key: str, value: str) -> dict:
    """같은 사용자의 같은 key는 새 행 대신 기존 값을 갱신합니다."""
    with psycopg.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
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
    return {"id": str(row[0]), "user_id": row[1], "key": row[2], "value": row[3]}


def list_memories(user_id: str) -> list[dict]:
    """user_id가 일치하는 장기 Memory만 조회합니다."""
    with psycopg.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, memory_key, memory_value FROM user_memories WHERE user_id = %s ORDER BY created_at",
            (user_id,),
        )
        return [{"id": str(row[0]), "key": row[1], "value": row[2]} for row in cursor.fetchall()]


def delete_memory(user_id: str, memory_id: str) -> bool:
    """사용자와 Memory ID가 모두 일치할 때만 삭제합니다."""
    with psycopg.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM user_memories WHERE user_id = %s AND id = %s", (user_id, memory_id))
        return cursor.rowcount == 1


if __name__ == "__main__":
    try:
        print("[06] PostgreSQL 장기 Memory\n")
        created = upsert_memory("student-01", "transportation", "대중교통")
        print("저장:", created)
        print("조회:", list_memories("student-01"))
        print("다른 사용자 삭제 차단(False):", delete_memory("student-02", created["id"]))
        print("본인 삭제 성공(True):", delete_memory("student-01", created["id"]))
        print("삭제 후:", list_memories("student-01"))
        print("\n핵심: 장기 Memory의 모든 SQL 조건에는 인증된 user_id가 포함되어야 합니다.")
    except psycopg.Error as error:
        print("\n[실행 실패] PostgreSQL에 연결하거나 Memory를 처리하지 못했습니다.")
        print("원인:", error)
        print("DATABASE_URL, PostgreSQL Container와 Schema 적용 여부를 확인하세요.")
        print("환경 점검: python .\00_check_environment.py")
