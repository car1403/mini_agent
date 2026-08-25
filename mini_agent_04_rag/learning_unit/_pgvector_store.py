"""11~15 예제가 공유하는 Ollama Embedding·pgvector 저장소입니다."""

import os
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import httpx
import psycopg
from dotenv import load_dotenv
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb


ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db",
)


def embed(text: str) -> list[float]:
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/embed",
        json={"model": EMBEDDING_MODEL, "input": text},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["embeddings"][0]


def connect():
    connection = psycopg.connect(DATABASE_URL)
    register_vector(connection)
    return connection


def delete_collection(collection: str) -> None:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM documents WHERE collection_name = %s", (collection,))


def delete_stale_source_chunks(*, collection: str, source: str, keep_count: int) -> int:
    """새 문서보다 뒤에 남은 이전 버전 Chunk를 제거합니다."""
    if keep_count < 0:
        raise ValueError("keep_count는 0 이상이어야 합니다.")
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM documents
            WHERE collection_name = %s
              AND source = %s
              AND chunk_index >= %s
            """,
            (collection, source, keep_count),
        )
        return cursor.rowcount


def upsert_text(
    *,
    collection: str,
    title: str,
    content: str,
    source: str,
    chunk_index: int = 0,
    metadata: dict[str, Any] | None = None,
) -> str:
    """같은 collection/source/chunk_index는 갱신하여 재색인 중복을 막습니다."""
    vector = embed(content)
    document_id = uuid5(NAMESPACE_URL, f"{collection}:{source}:{chunk_index}")
    with connect() as connection, connection.cursor() as cursor:
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
            (
                document_id,
                collection,
                title,
                content,
                source,
                chunk_index,
                EMBEDDING_MODEL,
                len(vector),
                vector,
                Jsonb(metadata or {}),
            ),
        )
    return str(document_id)


def similarity_search(
    query: str,
    *,
    collection: str,
    top_k: int = 3,
    score_threshold: float | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if top_k < 1:
        raise ValueError("top_k는 1 이상이어야 합니다.")
    vector = embed(query)
    metadata_filter = metadata_filter or {}
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, title, content, source, chunk_index, metadata,
                   1 - (embedding <=> %s) AS score
            FROM documents
            WHERE collection_name = %s
              AND embedding_provider = 'ollama'
              AND embedding_model = %s
              AND embedding_dimension = %s
              AND (%s::double precision IS NULL OR 1 - (embedding <=> %s) >= %s)
              AND (%s::jsonb = '{}'::jsonb OR metadata @> %s::jsonb)
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (
                vector,
                collection,
                EMBEDDING_MODEL,
                len(vector),
                score_threshold,
                vector,
                score_threshold,
                Jsonb(metadata_filter),
                Jsonb(metadata_filter),
                vector,
                top_k,
            ),
        )
        return [
            {
                "id": str(row[0]),
                "title": row[1],
                "content": row[2],
                "source": row[3],
                "chunk_index": row[4],
                "metadata": row[5],
                "score": float(row[6]),
            }
            for row in cursor.fetchall()
        ]

def list_documents(*, collection: str) -> list[dict[str, Any]]:
    """교육용 키워드·Hybrid 검색을 위해 Collection의 Chunk를 읽습니다."""
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, title, content, source, chunk_index, metadata
            FROM documents
            WHERE collection_name = %s
            ORDER BY source, chunk_index
            """,
            (collection,),
        )
        return [
            {
                "id": str(row[0]),
                "title": row[1],
                "content": row[2],
                "source": row[3],
                "chunk_index": row[4],
                "metadata": row[5],
            }
            for row in cursor.fetchall()
        ]
