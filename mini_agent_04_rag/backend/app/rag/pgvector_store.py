from uuid import NAMESPACE_URL, uuid5

import psycopg
from pgvector.psycopg import register_vector
from psycopg.types.json import Jsonb

from app.core.config import settings
from app.schemas import RagChunk, RagSearchItem


def connect():
    connection = psycopg.connect(settings.database_url)
    register_vector(connection)
    return connection


def reset_collection() -> None:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM documents WHERE collection_name = %s",
            (settings.rag_collection,),
        )


def delete_source(source: str) -> None:
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM documents WHERE collection_name = %s AND source = %s",
            (settings.rag_collection, source),
        )


def _upsert_chunk(cursor, chunk: RagChunk, vector: list[float]) -> None:
    """이미 열린 Transaction에서 Chunk 하나를 Upsert합니다."""
    document_id = uuid5(NAMESPACE_URL, f"{settings.rag_collection}:{chunk.chunk_id}")
    cursor.execute(
        """
        INSERT INTO documents
            (id, collection_name, title, content, source, chunk_index,
             embedding_provider, embedding_model, embedding_dimension,
             embedding, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, 'ollama', %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            source = EXCLUDED.source,
            chunk_index = EXCLUDED.chunk_index,
            embedding_provider = EXCLUDED.embedding_provider,
            embedding_model = EXCLUDED.embedding_model,
            embedding_dimension = EXCLUDED.embedding_dimension,
            embedding = EXCLUDED.embedding,
            metadata = EXCLUDED.metadata,
            created_at = NOW()
        """,
        (
            document_id, settings.rag_collection, chunk.title, chunk.text,
            chunk.source, chunk.chunk_index, settings.ollama_embedding_model,
            len(vector), vector, Jsonb({"chunk_id": chunk.chunk_id, **chunk.metadata}),
        ),
    )


def write_chunks(
    items: list[tuple[RagChunk, list[float]]],
    *,
    reset: bool = False,
    replace_source: str | None = None,
) -> None:
    """Collection/Source 정리와 모든 Upsert를 한 Transaction으로 처리합니다."""
    if reset and replace_source is not None:
        raise ValueError("reset과 replace_source는 동시에 사용할 수 없습니다.")
    if replace_source is not None and any(chunk.source != replace_source for chunk, _ in items):
        raise ValueError("replace_source와 다른 Source의 Chunk가 포함되어 있습니다.")

    with connect() as connection, connection.cursor() as cursor:
        if reset:
            cursor.execute(
                "DELETE FROM documents WHERE collection_name = %s",
                (settings.rag_collection,),
            )
        elif replace_source is not None:
            cursor.execute(
                "DELETE FROM documents WHERE collection_name = %s AND source = %s",
                (settings.rag_collection, replace_source),
            )
        for chunk, vector in items:
            _upsert_chunk(cursor, chunk, vector)


def add_chunk(chunk: RagChunk, vector: list[float]) -> None:
    """단일 Chunk도 공통 Transaction 경로로 저장합니다."""
    write_chunks([(chunk, vector)])


def vector_search(
    vector: list[float],
    top_k: int = 3,
    score_threshold: float | None = None,
    metadata_filter: dict | None = None,
) -> list[RagSearchItem]:
    minimum = settings.rag_min_score if score_threshold is None else score_threshold
    metadata_filter = metadata_filter or {}
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT title, content, source, chunk_index, metadata,
                   1 - (embedding <=> %s) AS score
            FROM documents
            WHERE collection_name = %s
              AND embedding_provider = 'ollama'
              AND embedding_model = %s
              AND embedding_dimension = %s
              AND 1 - (embedding <=> %s) >= %s
              AND (%s::jsonb = '{}'::jsonb OR metadata @> %s::jsonb)
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (
                vector, settings.rag_collection, settings.ollama_embedding_model,
                len(vector), vector, minimum, Jsonb(metadata_filter),
                Jsonb(metadata_filter), vector, top_k,
            ),
        )
        results = [
            RagSearchItem(
                title=row[0], content=row[1], source=row[2],
                chunk_index=row[3], metadata=row[4], score=round(float(row[5]), 3),
            )
            for row in cursor.fetchall()
        ]
        return results


def indexed_documents(metadata_filter: dict | None = None) -> list[RagSearchItem]:
    metadata_filter = metadata_filter or {}
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT title, content, source, chunk_index, metadata
            FROM documents
            WHERE collection_name = %s
              AND (%s::jsonb = '{}'::jsonb OR metadata @> %s::jsonb)
            ORDER BY source, chunk_index
            """,
            (settings.rag_collection, Jsonb(metadata_filter), Jsonb(metadata_filter)),
        )
        return [
            RagSearchItem(
                title=row[0], content=row[1], source=row[2], chunk_index=row[3],
                metadata=row[4], score=0,
            )
            for row in cursor.fetchall()
        ]


def source_documents(source: str) -> list[RagSearchItem]:
    """수업 화면에서 Source 교체 전후의 실제 pgvector Chunk를 관찰합니다."""
    with connect() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT title, content, source, chunk_index, metadata
            FROM documents
            WHERE collection_name = %s AND source = %s
            ORDER BY chunk_index
            """,
            (settings.rag_collection, source),
        )
        return [
            RagSearchItem(
                title=row[0], content=row[1], source=row[2], chunk_index=row[3],
                metadata=row[4], score=0,
            )
            for row in cursor.fetchall()
        ]
