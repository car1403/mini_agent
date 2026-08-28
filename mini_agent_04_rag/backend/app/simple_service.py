"""검색, Context 구성, 답변 생성을 순서대로 보여주는 간단한 RAG Service입니다."""

import re

import httpx

from app.core.config import settings
from app.rag import redis_cache
from app.rag.embedding import embed
from app.rag.keyword_store import all_chunks, keyword_search
from app.rag.pgvector_store import indexed_documents, vector_search, write_chunks
from app.schemas import AnswerResult, IndexResult, RagChunk, SearchItem


def keyword_search_indexed(
    question: str,
    top_k: int,
    metadata_filter: dict,
) -> list[SearchItem]:
    question_words = set(re.findall(r"[가-힣A-Za-z0-9-]+", question.lower()))
    results = []

    for item in indexed_documents(metadata_filter):
        document_words = set(
            re.findall(r"[가-힣A-Za-z0-9-]+", f"{item.title} {item.content}".lower())
        )
        common_words = question_words & document_words
        if common_words:
            item.score = len(common_words) / max(len(question_words), 1)
            results.append(item)

    results.sort(key=lambda item: item.score, reverse=True)
    return results[:top_k]


def search_documents(
    question: str,
    mode: str,
    top_k: int,
    score_threshold: float | None = None,
    metadata_filter: dict | None = None,
) -> list[SearchItem]:
    """선택한 검색 방식으로 관련 문서를 찾습니다."""
    metadata_filter = metadata_filter or {}

    if mode == "keyword":
        if metadata_filter:
            return keyword_search_indexed(question, top_k, metadata_filter)
        return keyword_search(question, top_k)

    if mode == "pgvector":
        return vector_search(
            embed(question),
            top_k,
            score_threshold,
            metadata_filter,
        )

    if mode == "hybrid":
        keyword_results = keyword_search_indexed(question, top_k, metadata_filter)
        vector_results = vector_search(
            embed(question),
            top_k,
            score_threshold,
            metadata_filter,
        )
        combined = {}
        for item in keyword_results + vector_results:
            key = (item.source, item.chunk_index)
            combined[key] = item
        return list(combined.values())[:top_k]

    raise ValueError(f"지원하지 않는 검색 방식입니다: {mode}")


def index_example_documents() -> IndexResult:
    """기본 여행 문서를 Embedding하여 pgvector에 저장합니다."""
    chunks = all_chunks()
    items = [(chunk, embed(chunk.text)) for chunk in chunks]
    write_chunks(items, reset=True)
    try:
        redis_cache.invalidate_answer_cache()
    except Exception:
        # Redis가 꺼져 있어도 문서 색인은 정상적으로 끝나야 합니다.
        pass
    return IndexResult(
        collection=settings.rag_collection,
        indexed_count=len(chunks),
        embedding_model=settings.ollama_embedding_model,
    )


def index_custom_chunks(chunks: list[RagChunk], source: str) -> IndexResult:
    """직접 입력하거나 PDF에서 만든 Chunk를 pgvector에 저장합니다."""
    items = [(chunk, embed(chunk.text)) for chunk in chunks]
    write_chunks(items, replace_source=source)
    try:
        redis_cache.invalidate_answer_cache()
    except Exception:
        # Redis는 선택 기능이므로 PDF/문서 색인을 막지 않습니다.
        pass
    return IndexResult(
        collection=settings.rag_collection,
        indexed_count=len(chunks),
        embedding_model=settings.ollama_embedding_model,
        source=source,
    )


def make_context(results: list[SearchItem]) -> str:
    return "\n".join(
        f"[{item.source}] {item.content}"
        for item in results
    )


def ask_ollama(question: str, context: str) -> str:
    response = httpx.post(
        f"{settings.ollama_base_url}/api/chat",
        json={
            "model": settings.ollama_model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": "Context만 사용해 한국어로 답하고 출처를 표시하세요.",
                },
                {
                    "role": "user",
                    "content": f"질문: {question}\n\nContext:\n{context}",
                },
            ],
        },
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def answer_question(
    question: str,
    mode: str,
    top_k: int,
    use_ollama: bool,
    use_cache: bool,
    score_threshold: float | None = None,
    metadata_filter: dict | None = None,
) -> AnswerResult:
    """Cache 확인 → 검색 → Context → 답변 순서로 실행합니다."""
    metadata_filter = metadata_filter or {}
    cache_key = redis_cache.make_key(
        question,
        mode,
        top_k,
        "ollama" if use_ollama else "mock",
        score_threshold,
        metadata_filter,
    )

    if use_cache:
        try:
            cached, ttl = redis_cache.get(cache_key)
            if cached:
                cached["cache_hit"] = True
                cached["cache_ttl_seconds"] = max(ttl, 0)
                return AnswerResult.model_validate(cached)
        except Exception:
            pass

    results = search_documents(
        question,
        mode,
        top_k,
        score_threshold,
        metadata_filter,
    )
    if not results:
        return AnswerResult(
            answer="관련 문서에서 근거를 찾지 못했습니다.",
            grounded=False,
            mode=mode,
        )

    context = make_context(results)
    answer = ask_ollama(question, context) if use_ollama else results[0].content
    result = AnswerResult(
        answer=answer,
        grounded=True,
        mode=mode,
        context=context,
        sources=sorted({item.source for item in results}),
        results=results,
    )

    if use_cache:
        try:
            result.cache_ttl_seconds = redis_cache.set(
                cache_key,
                result.model_dump(mode="json"),
            )
        except Exception:
            pass
    return result
