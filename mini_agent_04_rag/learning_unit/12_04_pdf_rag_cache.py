"""사용자가 같은 질문을 두 번 했을 때 Redis Cache가 동작하는 흐름입니다."""

import os
from typing import Any

import httpx

from _pgvector_store import (
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    similarity_search,
)
from _redis_cache import DEFAULT_TTL_SECONDS, JsonCache, cache_key


COLLECTION = "rag_pdf_lesson"
CHAT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
CACHE_NAMESPACE = "pdf-rag-answer:v1"
QUESTION = "당일 취소 규정은 어떻게 되나요?"
TOP_K = 3


def generate_pdf_answer(question: str) -> dict[str, Any]:
    results = similarity_search(
        question,
        collection=COLLECTION,
        top_k=TOP_K,
    )
    if not results:
        return {
            "answer": "PDF에서 질문과 관련된 근거를 찾지 못했습니다.",
            "sources": [],
        }

    context = "\n".join(
        f"[{item['source']} p.{item['metadata'].get('page_number', '?')}] "
        f"{item['content']}"
        for item in results
    )
    response = httpx.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": CHAT_MODEL,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "제공된 PDF Context만 사용해 한국어로 답하세요. "
                        "근거가 부족하면 모른다고 답하고 출처 페이지를 표시하세요."
                    ),
                },
                {
                    "role": "user",
                    "content": f"질문: {question}\n\nPDF Context:\n{context}",
                },
            ],
        },
        timeout=120,
    )
    response.raise_for_status()
    return {
        "answer": response.json()["message"]["content"],
        "sources": sorted({
            f"{item['source']} p.{item['metadata'].get('page_number', '?')}"
            for item in results
        }),
    }


def ask_pdf(
    question: str,
    cache: JsonCache,
) -> dict[str, Any]:
    """Cache가 있으면 바로 반환하고, 없으면 RAG 답변을 생성해 저장합니다."""
    key = cache_key(CACHE_NAMESPACE, {
        "collection": COLLECTION,
        "embedding_model": EMBEDDING_MODEL,
        "chat_model": CHAT_MODEL,
        "question": question,
        "top_k": TOP_K,
    })
    cached = cache.get(key)
    if cached is not None:
        return {
            **cached,
            "cache_hit": True,
            "cache_ttl_seconds": cache.ttl(key),
        }

    result = generate_pdf_answer(question)
    cache_saved = cache.set(
        key,
        result,
        ttl_seconds=DEFAULT_TTL_SECONDS,
    )
    return {
        **result,
        "cache_hit": False,
        "cache_saved": cache_saved,
        "cache_ttl_seconds": cache.ttl(key) if cache_saved else None,
    }


if __name__ == "__main__":
    redis_cache = JsonCache()

    # 실행할 때마다 MISS → HIT 흐름을 관찰하기 위한 교육용 초기화입니다.
    redis_cache.delete_namespace(CACHE_NAMESPACE)

    print("=== 사용자의 1차 질문 ===")
    print(f"사용자: {QUESTION}")
    first = ask_pdf(QUESTION, redis_cache)
    if first["cache_hit"]:
        print("처리: 기존 Redis Cache에서 답변 반환")
    else:
        print("처리: Redis MISS → pgvector 검색 → Ollama 답변 → Redis 저장")
    print(f"답변: {first['answer']}")
    print(f"Cache 저장: {first.get('cache_saved', True)}")

    print("\n=== 동일한 사용자의 2차 질문 ===")
    print(f"사용자: {QUESTION}")
    second = ask_pdf(QUESTION, redis_cache)
    if second["cache_hit"]:
        print("처리: Redis HIT → 저장된 답변을 즉시 반환")
    else:
        print("처리: Redis 연결 또는 저장 실패 → RAG를 다시 실행")
    print(f"답변: {second['answer']}")
    print(f"Cache 남은 시간: {second['cache_ttl_seconds']}초")
