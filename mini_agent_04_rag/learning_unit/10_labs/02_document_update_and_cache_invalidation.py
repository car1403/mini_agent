"""정책 문서 갱신, 오래된 pgvector Chunk 제거, Redis 무효화 Workflow.

문서 갱신 순서는 Backend가 결정해야 하므로 Agent가 아닌 결정적 Workflow입니다.
"""

import json
import sys
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _pgvector_store import (
    delete_collection,
    delete_stale_source_chunks,
    list_documents,
    similarity_search,
    upsert_text,
)
from _redis_cache import JsonCache, cache_key


COLLECTION = "rag_document_update_lab"
SOURCE = "hotel-refund.md"
CACHE_NAMESPACE = "document-update-answer"
QUESTION = "호텔을 당일 취소하면 환불받을 수 있나요?"

VERSION_1 = [
    "체크인 3일 전까지 취소하면 전액 환불합니다.",
    "체크인 당일에는 숙박 요금의 50%를 환불합니다.",
]
VERSION_2 = [
    "체크인 당일 취소에는 숙박 요금 전액이 부과되며 환불되지 않습니다.",
]


def index_document(chunks: list[str], *, version: int, cache: JsonCache) -> dict[str, Any]:
    """새 Chunk를 Upsert한 뒤 이전 버전에서 남은 뒤쪽 Chunk를 제거합니다."""
    for chunk_index, content in enumerate(chunks):
        upsert_text(
            collection=COLLECTION,
            title="호텔 환불 정책",
            content=content,
            source=SOURCE,
            chunk_index=chunk_index,
            metadata={"status": "active", "document_version": version},
        )
    stale_count = delete_stale_source_chunks(
        collection=COLLECTION,
        source=SOURCE,
        keep_count=len(chunks),
    )
    invalidated = cache.delete_namespace(CACHE_NAMESPACE)
    return {
        "upserted": len(chunks), "deleted_stale_chunks": stale_count,
        "invalidated_cache_keys": invalidated, "version": version,
    }


def cached_search(cache: JsonCache) -> dict[str, Any]:
    key = cache_key(CACHE_NAMESPACE, {
        "collection": COLLECTION,
        "question": QUESTION,
        "top_k": 2,
    })
    cached = cache.get(key)
    if cached is not None:
        return {**cached, "cache_hit": True, "cache_ttl_seconds": cache.ttl(key)}

    results = similarity_search(QUESTION, collection=COLLECTION, top_k=2)
    value = {
        "results": results,
        "cache_hit": False,
    }
    cache_saved = cache.set(key, value)
    return {
        **value,
        "cache_saved": cache_saved,
        "cache_ttl_seconds": cache.ttl(key) if cache_saved else None,
    }


def summarize_documents() -> list[dict[str, Any]]:
    return [
        {
            "chunk_index": item["chunk_index"],
            "content": item["content"],
            "metadata": item["metadata"],
        }
        for item in list_documents(collection=COLLECTION)
    ]


if __name__ == "__main__":
    redis_cache = JsonCache()
    delete_collection(COLLECTION)

    print("[1] 문서 version 1 색인")
    print(index_document(VERSION_1, version=1, cache=redis_cache))
    print(json.dumps(summarize_documents(), ensure_ascii=False, indent=2))

    print("\n[2] version 1 검색 Cache MISS → HIT")
    print(json.dumps(cached_search(redis_cache), ensure_ascii=False, indent=2))
    print(json.dumps(cached_search(redis_cache), ensure_ascii=False, indent=2))

    print("\n[3] 문서 version 2 갱신과 오래된 Chunk 제거")
    print(index_document(VERSION_2, version=2, cache=redis_cache))
    print(json.dumps(summarize_documents(), ensure_ascii=False, indent=2))

    print("\n[4] 새 정책 검색—무효화 후 다시 Cache MISS")
    print(json.dumps(cached_search(redis_cache), ensure_ascii=False, indent=2))

