"""PDF 페이지별 Chunk를 pgvector에 저장하고 Redis로 검색을 캐싱하는 Lab."""

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

from pypdf import PdfReader


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _pgvector_store import delete_stale_source_chunks, similarity_search, upsert_text
from _redis_cache import JsonCache, cache_key


COLLECTION = "rag_pdf_travel_guide_lab"
CACHE_NAMESPACE = "pdf-travel-guide"


def split_text(text: str, *, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap은 0 이상 chunk_size 미만이어야 합니다.")
    normalized = re.sub(r"[ \t]+", " ", text).strip()
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        if end < len(normalized):
            boundary = max(normalized.rfind("\n", start, end), normalized.rfind(". ", start, end))
            if boundary > start + chunk_size // 2:
                end = boundary + 1
        chunks.append(normalized[start:end].strip())
        if end == len(normalized):
            break
        start = end - overlap
    return [chunk for chunk in chunks if chunk]


def index_pdf(pdf_path: Path, cache: JsonCache) -> dict[str, Any]:
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"텍스트형 PDF 파일을 찾을 수 없습니다: {pdf_path}")
    file_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    # 절대 경로 Hash를 Source ID에 넣어 같은 파일명의 서로 다른 문서 충돌을 막습니다.
    path_hash = hashlib.sha256(str(pdf_path.resolve()).encode("utf-8")).hexdigest()[:12]
    source_id = f"{pdf_path.name}:{path_hash}"
    reader = PdfReader(pdf_path)
    total = 0
    for page_number, page in enumerate(reader.pages, start=1):
        for page_chunk_index, content in enumerate(split_text(page.extract_text() or "")):
            upsert_text(
                collection=COLLECTION,
                title=pdf_path.stem,
                content=content,
                source=source_id,
                chunk_index=total,
                metadata={
                    "display_source": pdf_path.name,
                    "source_id": source_id,
                    "page_number": page_number,
                    "page_chunk_index": page_chunk_index,
                    "file_sha256": file_hash,
                    "status": "active",
                },
            )
            total += 1
    if total == 0:
        raise ValueError("PDF에서 텍스트를 추출하지 못했습니다. 스캔 PDF에는 OCR이 필요합니다.")
    stale = delete_stale_source_chunks(collection=COLLECTION, source=source_id, keep_count=total)
    invalidated = cache.delete_namespace(CACHE_NAMESPACE)
    return {
        "source_id": source_id,
        "indexed_chunks": total,
        "deleted_stale_chunks": stale,
        "invalidated_cache_keys": invalidated,
    }


def cached_search(query: str, source_id: str, cache: JsonCache, *, top_k: int = 3) -> dict[str, Any]:
    payload = {"collection": COLLECTION, "source_id": source_id, "query": query, "top_k": top_k}
    key = cache_key(CACHE_NAMESPACE, payload)
    cached = cache.get(key)
    if cached is not None:
        return {**cached, "cache_hit": True, "cache_ttl_seconds": cache.ttl(key)}
    results = similarity_search(
        query,
        collection=COLLECTION,
        top_k=top_k,
        metadata_filter={"source_id": source_id, "status": "active"},
    )
    value = {"results": results}
    saved = cache.set(key, value)
    return {**value, "cache_hit": False, "cache_saved": saved}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path, help="색인할 텍스트형 여행 가이드 PDF")
    parser.add_argument("--query", default="추천 관광지는 어디인가요?")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    redis_cache = JsonCache()
    indexed = index_pdf(args.pdf, redis_cache)
    print("색인:", indexed)
    result = cached_search(args.query, indexed["source_id"], redis_cache)
    for item in result["results"]:
        metadata = item["metadata"]
        print(f"{item['score']:.3f} | {metadata['display_source']} p.{metadata['page_number']} | {item['content']}")
    print("cache_hit:", result["cache_hit"])

