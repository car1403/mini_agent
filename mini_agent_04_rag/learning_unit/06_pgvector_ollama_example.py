"""Ollama Embedding을 pgvector에 저장하고 실제 의미 검색을 수행합니다."""

import os
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

import httpx
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db")
COLLECTION = "rag_lesson"

DOCUMENTS = [
    ("호텔 환불", "체크인 3일 전까지 취소하면 전액 환불합니다.", "hotel-refund.md"),
    ("수하물", "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다.", "baggage.md"),
    ("관광지 운영", "바다 박물관은 매주 화요일에 휴관합니다.", "attraction-hours.md"),
]


def embed(text: str) -> list[float]:
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={"model": OLLAMA_EMBEDDING_MODEL, "input": text},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embeddings"][0]


def connect():
    connection = psycopg.connect(DATABASE_URL)
    register_vector(connection)
    return connection


def index_documents() -> None:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM documents WHERE collection_name = %s", (COLLECTION,))
        for index, (title, content, source) in enumerate(DOCUMENTS):
            vector = embed(content)
            # 같은 문서를 다시 색인해도 중복되지 않는 결정적 ID를 사용합니다.
            document_id = uuid5(NAMESPACE_URL, f"{COLLECTION}:{source}:{index}")
            cursor.execute(
                """
                INSERT INTO documents
                    (id, collection_name, title, content, source, chunk_index,
                     embedding_provider, embedding_model, embedding_dimension, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, 'ollama', %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    content = EXCLUDED.content,
                    embedding_model = EXCLUDED.embedding_model,
                    embedding_dimension = EXCLUDED.embedding_dimension,
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    created_at = NOW()
                """,
                (document_id, COLLECTION, title, content, source, index,
                 OLLAMA_EMBEDDING_MODEL, len(vector), vector, Jsonb({"lesson": "04_rag"})),
            )


def search(question: str, top_k: int = 3) -> list[dict]:
    vector = embed(question)
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT title, content, source, 1 - (embedding <=> %s) AS score
            FROM documents
            WHERE collection_name = %s
              AND embedding_provider = 'ollama'
              AND embedding_model = %s
              AND embedding_dimension = %s
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (vector, COLLECTION, OLLAMA_EMBEDDING_MODEL, len(vector), vector, top_k),
        )
        return [
            {"title": row[0], "content": row[1], "source": row[2], "score": float(row[3])}
            for row in cursor.fetchall()
        ]


if __name__ == "__main__":
    index_documents()
    for item in search("숙소 예약을 취소하면 돈을 돌려받을 수 있나요?"):
        print(f"{item['score']:.3f} | {item['source']} | {item['content']}")
