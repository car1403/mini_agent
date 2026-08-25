import pytest

from app.rag import pgvector_store, service
from app.schemas import RagChunk


def chunks(source: str = "policy.md") -> list[RagChunk]:
    return [
        RagChunk(
            chunk_id=f"{source}:0", text="첫 정책", source=source,
            title="정책", chunk_index=0,
        ),
        RagChunk(
            chunk_id=f"{source}:1", text="두 번째 정책", source=source,
            title="정책", chunk_index=1,
        ),
    ]


def test_embedding_failure_does_not_touch_database_or_cache(monkeypatch) -> None:
    calls: list[str] = []

    def failing_embed(text: str) -> list[float]:
        calls.append(f"embed:{text}")
        if text == "두 번째 정책":
            raise RuntimeError("embedding unavailable")
        return [1.0, 0.0]

    monkeypatch.setattr(service, "embed", failing_embed)
    monkeypatch.setattr(service, "write_chunks", lambda *args, **kwargs: calls.append("db"))
    monkeypatch.setattr(
        service.redis_cache,
        "invalidate_answer_cache",
        lambda: calls.append("cache"),
    )

    with pytest.raises(RuntimeError, match="embedding unavailable"):
        service.index_chunks(chunks(), source="policy.md", replace_source=True)

    assert calls == ["embed:첫 정책", "embed:두 번째 정책"]


def test_successful_ingestion_writes_once_then_invalidates_cache(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        service,
        "embed",
        lambda text: calls.append(f"embed:{text}") or [1.0, 0.0],
    )

    def write(items, *, reset=False, replace_source=None) -> None:
        assert len(items) == 2
        assert reset is False
        assert replace_source == "policy.md"
        calls.append("db_transaction")

    monkeypatch.setattr(service, "write_chunks", write)
    monkeypatch.setattr(
        service.redis_cache,
        "invalidate_answer_cache",
        lambda: calls.append("cache_invalidation") or 1,
    )

    result = service.index_chunks(chunks(), source="policy.md", replace_source=True)

    assert result.indexed_count == 2
    assert result.source == "policy.md"
    assert result.source == "policy.md"
    assert calls == [
        "embed:첫 정책",
        "embed:두 번째 정책",
        "db_transaction",
        "cache_invalidation",
    ]


def test_source_mismatch_is_rejected_before_embedding(monkeypatch) -> None:
    monkeypatch.setattr(
        service,
        "embed",
        lambda text: pytest.fail("Source 검증 전에 Embedding을 실행하면 안 됩니다."),
    )
    with pytest.raises(ValueError, match="다른 Chunk"):
        service.index_chunks(chunks("other.md"), source="policy.md", replace_source=True)


def test_transaction_writer_rejects_conflicting_scope() -> None:
    items = [(chunks()[0], [1.0, 0.0])]
    with pytest.raises(ValueError, match="동시에"):
        pgvector_store.write_chunks(items, reset=True, replace_source="policy.md")


def test_transaction_writer_rejects_other_source() -> None:
    items = [(chunks("other.md")[0], [1.0, 0.0])]
    with pytest.raises(ValueError, match="다른 Source"):
        pgvector_store.write_chunks(items, replace_source="policy.md")
