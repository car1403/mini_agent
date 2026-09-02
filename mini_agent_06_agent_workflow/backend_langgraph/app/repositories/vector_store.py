from typing import Any
from uuid import uuid4

import psycopg
from pgvector.psycopg import register_vector


class PgVectorStore:
    """Embedding 생성과 저장을 분리한 최소 pgvector Repository입니다."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self):
        connection = psycopg.connect(self.database_url)
        register_vector(connection)
        return connection

    def add(
        self,
        *,
        collection: str,
        title: str,
        content: str,
        source: str,
        embedding: list[float],
        embedding_provider: str,
        embedding_model: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        document_id = uuid4()
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents
                    (id, collection_name, title, content, source, chunk_index,
                     embedding_provider, embedding_model, embedding_dimension,
                     embedding, metadata)
                VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, %s, %s)
                """,
                (
                    document_id,
                    collection,
                    title,
                    content,
                    source,
                    embedding_provider,
                    embedding_model,
                    len(embedding),
                    embedding,
                    metadata or {},
                ),
            )
        return str(document_id)

    def search(
        self,
        *,
        collection: str,
        embedding: list[float],
        embedding_provider: str,
        embedding_model: str,
        limit: int = 3,
    ) -> list[dict]:
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, content, source, 1 - (embedding <=> %s) AS score
                FROM documents
                WHERE collection_name = %s
                  AND embedding_provider = %s
                  AND embedding_model = %s
                  AND embedding_dimension = %s
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (
                    embedding,
                    collection,
                    embedding_provider,
                    embedding_model,
                    len(embedding),
                    embedding,
                    limit,
                ),
            )
            rows = cursor.fetchall()
        return [
            {
                "id": str(row[0]),
                "title": row[1],
                "content": row[2],
                "source": row[3],
                "score": float(row[4]),
            }
            for row in rows
        ]
