"""상품 카테고리·가격 조건과 Hybrid Search를 결합하는 pgvector Lab."""

import re
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _pgvector_store import delete_collection, list_documents, similarity_search, upsert_text
from _redis_cache import JsonCache, cache_key


COLLECTION = "rag_product_search_lab"
CACHE_NAMESPACE = "product-hybrid-search"
PRODUCTS = [
    ("RUN-100", "초경량 러닝화로 장거리 달리기에 적합합니다.", "shoes", 89000),
    ("TRAIL-20", "접지력이 높은 방수 트레일 러닝화입니다.", "shoes", 129000),
    ("WALK-7", "쿠션이 부드러운 일상용 워킹화입니다.", "shoes", 69000),
    ("BAG-15", "15리터 러닝 백팩으로 물통 수납이 가능합니다.", "bag", 59000),
]


class ProductSearchArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=2, max_length=300)
    category: str | None = Field(default=None, pattern=r"^[a-z]+$")
    max_price: int | None = Field(default=None, ge=0, le=10_000_000)
    top_k: int = Field(default=3, ge=1, le=10)


def prepare_products(cache: JsonCache) -> None:
    delete_collection(COLLECTION)
    for index, (sku, description, category, price) in enumerate(PRODUCTS):
        upsert_text(
            collection=COLLECTION,
            title=sku,
            content=f"상품 코드 {sku}. {description} 가격 {price:,}원.",
            source="product-catalog.json",
            chunk_index=index,
            metadata={"sku": sku, "category": category, "price": price, "status": "active"},
        )
    cache.delete_namespace(CACHE_NAMESPACE)


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[가-힣A-Za-z0-9-]+", text.lower()))


def allowed(item: dict[str, Any], arguments: ProductSearchArguments) -> bool:
    metadata = item["metadata"]
    return (
        (arguments.category is None or metadata["category"] == arguments.category)
        and (arguments.max_price is None or metadata["price"] <= arguments.max_price)
        and metadata["status"] == "active"
    )


def keyword_search(arguments: ProductSearchArguments) -> list[dict[str, Any]]:
    query_tokens = tokenize(arguments.query)
    ranked = []
    for item in list_documents(collection=COLLECTION):
        if not allowed(item, arguments):
            continue
        common = query_tokens & tokenize(f"{item['title']} {item['content']}")
        if common:
            ranked.append({**item, "score": len(common) / max(len(query_tokens), 1)})
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[: arguments.top_k]


def vector_search(arguments: ProductSearchArguments) -> list[dict[str, Any]]:
    metadata_filter = {"status": "active"}
    if arguments.category:
        metadata_filter["category"] = arguments.category
    candidates = similarity_search(
        arguments.query,
        collection=COLLECTION,
        top_k=20,
        metadata_filter=metadata_filter,
    )
    return [item for item in candidates if allowed(item, arguments)][: arguments.top_k]


def rrf(groups: list[list[dict[str, Any]]], *, top_k: int) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
    for results in groups:
        for rank, item in enumerate(results, start=1):
            current = fused.setdefault(item["id"], {**item, "rrf_score": 0.0})
            current["rrf_score"] += 1 / (60 + rank)
    return sorted(fused.values(), key=lambda item: item["rrf_score"], reverse=True)[:top_k]


def hybrid_search(arguments: ProductSearchArguments, cache: JsonCache) -> dict[str, Any]:
    key = cache_key(CACHE_NAMESPACE, arguments.model_dump())
    cached = cache.get(key)
    if cached is not None:
        return {**cached, "cache_hit": True, "cache_ttl_seconds": cache.ttl(key)}

    keyword = keyword_search(arguments)
    vector = vector_search(arguments)
    value = {
        "keyword": keyword,
        "vector": vector,
        "hybrid": rrf([keyword, vector], top_k=arguments.top_k),
    }
    saved = cache.set(key, value)
    return {**value, "cache_hit": False, "cache_saved": saved}


if __name__ == "__main__":
    redis_cache = JsonCache()
    prepare_products(redis_cache)
    search_arguments = ProductSearchArguments(
        query="10만원 이하 가벼운 장거리 달리기 신발",
        category="shoes",
        max_price=100_000,
        top_k=3,
    )
    result = hybrid_search(search_arguments, redis_cache)
    print("검색 조건:", search_arguments.model_dump())
    for mode in ("keyword", "vector", "hybrid"):
        print(f"\n[{mode}]")
        for item in result[mode]:
            score = item.get("rrf_score", item.get("score", 0.0))
            print(f"{score:.4f} | {item['metadata']['sku']} | {item['metadata']['price']:,}원 | {item['content']}")
    print("\nCache:", {key: result.get(key) for key in ("cache_hit", "cache_saved")})

