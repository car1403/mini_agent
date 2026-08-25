from time import perf_counter
import re
from typing import Any

from app.core.config import settings
from app.services.generation_service import generate
from app.rag.documents import TRAVEL_DOCUMENTS
from app.rag.embedding import embed
from app.rag.keyword_store import all_chunks, keyword_search
from app.rag.pgvector_store import (
    indexed_documents, vector_search, write_chunks,
)
from app.rag import redis_cache
from app.schemas import RagAnswerResult, RagChunk, RagIndexResult, RagSearchItem


def _indexed_keyword_search(
    query: str, top_k: int, metadata_filter: dict[str, Any],
) -> list[RagSearchItem]:
    query_tokens = set(re.findall(r"[가-힣A-Za-z0-9-]+", query.lower()))
    results = []
    for item in indexed_documents(metadata_filter):
        tokens = set(re.findall(r"[가-힣A-Za-z0-9-]+", f"{item.title} {item.content}".lower()))
        common = query_tokens & tokens
        if common:
            item.score = round(len(common) / max(len(query_tokens), 1), 3)
            results.append(item)
    return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]


def _hybrid_search(
    query: str, top_k: int, score_threshold: float | None,
    metadata_filter: dict[str, Any],
) -> list[RagSearchItem]:
    candidates = min(max(top_k * 3, 10), 30)
    keyword = _indexed_keyword_search(query, candidates, metadata_filter)
    vector = vector_search(embed(query), candidates, score_threshold, metadata_filter)
    fused: dict[tuple[str, int], dict[str, Any]] = {}
    for mode, results in (("keyword", keyword), ("pgvector", vector)):
        for rank, item in enumerate(results, start=1):
            key = (item.source, item.chunk_index)
            entry = fused.setdefault(key, {
                "item": item, "score": 0.0, "matched_by": [],
                "keyword_rank": None, "vector_rank": None,
            })
            entry["score"] += 1 / (60 + rank)
            entry["matched_by"].append(mode)
            if mode == "keyword":
                entry["keyword_rank"] = rank
            else:
                entry["vector_rank"] = rank
    ordered = sorted(fused.values(), key=lambda entry: entry["score"], reverse=True)[:top_k]
    output = []
    for entry in ordered:
        item = entry["item"]
        item.score = round(entry["score"], 6)
        item.matched_by = entry["matched_by"]
        item.keyword_rank = entry["keyword_rank"]
        item.vector_rank = entry["vector_rank"]
        output.append(item)
    return output


def search(
    query: str,
    mode: str,
    top_k: int,
    score_threshold: float | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> list[RagSearchItem]:
    metadata_filter = metadata_filter or {}
    if mode == "keyword":
        if metadata_filter:
            return _indexed_keyword_search(query, top_k, metadata_filter)
        # 기본 keyword 경로는 Docker 없는 첫 실습을 위해 메모리 문서를 사용합니다.
        return keyword_search(query, top_k)
    if mode == "pgvector":
        return vector_search(embed(query), top_k, score_threshold, metadata_filter)
    if mode == "hybrid":
        return _hybrid_search(query, top_k, score_threshold, metadata_filter)
    raise ValueError(f"지원하지 않는 검색 방식입니다: {mode}")


def index_documents(reset: bool = True) -> RagIndexResult:
    chunks = all_chunks()
    # 외부 Embedding이 모두 성공한 뒤에만 DB Transaction을 시작합니다.
    items = [(chunk, embed(chunk.text)) for chunk in chunks]
    write_chunks(items, reset=reset)
    # 문서 변경 후에는 이전 Context로 만든 답변 Cache를 재사용하지 않습니다.
    try:
        redis_cache.invalidate_answer_cache()
    except Exception:
        # Redis가 없어도 영구 Vector 색인 자체는 완료할 수 있습니다.
        pass
    return RagIndexResult(
        collection=settings.rag_collection,
        indexed_count=len(chunks),
        embedding_model=settings.ollama_embedding_model,
    )


def index_chunks(chunks: list[RagChunk], *, source: str, replace_source: bool = True) -> RagIndexResult:
    if not chunks:
        raise ValueError("색인할 Chunk가 없습니다.")
    if any(chunk.source != source for chunk in chunks):
        raise ValueError("요청 Source와 다른 Chunk가 포함되어 있습니다.")
    # 실패할 수 있는 Embedding을 먼저 완료하여 기존 문서를 보존합니다.
    items = [(chunk, embed(chunk.text)) for chunk in chunks]
    write_chunks(items, replace_source=source if replace_source else None)
    try:
        redis_cache.invalidate_answer_cache()
    except Exception:
        pass
    return RagIndexResult(
        collection=settings.rag_collection,
        indexed_count=len(chunks),
        embedding_model=settings.ollama_embedding_model,
        source=source,
    )


def answer(
    query: str, mode: str, top_k: int, provider: str, use_cache: bool = True,
    score_threshold: float | None = None,
    metadata_filter: dict[str, Any] | None = None,
) -> RagAnswerResult:
    metadata_filter = metadata_filter or {}
    cache_key = redis_cache.make_key(
        query, mode, top_k, provider, score_threshold, metadata_filter,
    )
    if use_cache:
        try:
            cached, ttl = redis_cache.get(cache_key)
            if cached:
                cached["cache_hit"] = True
                cached["cache_ttl_seconds"] = max(ttl, 0)
                cached["trace"] = [{"stage": "cache", "data": {"hit": True, "ttl": ttl}}]
                return RagAnswerResult.model_validate(cached)
        except Exception:
            # Cache 장애가 검색과 답변 생성까지 막아서는 안 됩니다.
            pass

    started = perf_counter()
    results = search(query, mode, top_k, score_threshold, metadata_filter)
    retrieval_ms = round((perf_counter() - started) * 1000)
    trace = [
        {"stage": "cache", "data": {"hit": False, "enabled": use_cache}},
        {"stage": "retrieval", "data": {"mode": mode, "count": len(results), "latency_ms": retrieval_ms, "score_threshold": score_threshold, "metadata_filter": metadata_filter}},
    ]
    if not results:
        return RagAnswerResult(
            answer="제공된 여행 정책 문서에서 근거를 찾지 못했습니다.",
            grounded=False,
            provider=provider,
            search_mode=mode,
            trace=trace + [{"stage": "finish", "data": {"reason": "no_grounding"}}],
        )

    context = "\n".join(
        f"[{item.source}] {item.content}" for item in results
    )
    sources = sorted({item.source for item in results})
    if provider == "mock":
        answer_text = results[0].content
        generation_ms = 0
    else:
        prompt = f"질문: {query}\n\nContext:\n{context}"
        system_prompt = (
            "Context에 있는 내용만 사용해 한국어로 답하세요. "
            "Context에 근거가 없으면 모른다고 답하세요."
        )
        generation_started = perf_counter()
        answer_text = str(generate(provider, system_prompt, prompt).content)
        generation_ms = round((perf_counter() - generation_started) * 1000)

    result = RagAnswerResult(
        answer=answer_text,
        grounded=True,
        provider=provider,
        search_mode=mode,
        context=context,
        sources=sources,
        results=results,
        trace=trace + [
            {"stage": "context", "data": {"sources": sources, "characters": len(context)}},
            {"stage": "generation", "data": {"provider": provider, "latency_ms": generation_ms}},
        ],
    )
    if use_cache:
        try:
            result.cache_ttl_seconds = redis_cache.set(cache_key, result.model_dump(mode="json"))
            result.trace.append({"stage": "cache_write", "data": {"ttl": result.cache_ttl_seconds}})
        except Exception as error:
            result.trace.append({"stage": "cache_write", "data": {"error": str(error)}})
    return result
