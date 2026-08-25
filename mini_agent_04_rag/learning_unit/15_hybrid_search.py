"""키워드 검색과 pgvector 의미 검색의 순위를 RRF로 결합합니다."""

import re
from typing import Any

from _pgvector_store import delete_collection, list_documents, similarity_search, upsert_text


COLLECTION = "rag_hybrid_lesson"
DOCUMENTS = [
    ("A-1703 객실은 반려동물 동반 시 1박당 3만 원이 추가됩니다.", "room-a-1703.md"),
    ("반려견과 함께 머무는 펫 프렌들리 객실에는 추가 요금이 있습니다.", "pet-room.md"),
    ("일반 객실의 체크아웃 시간은 오전 11시입니다.", "checkout.md"),
]


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[가-힣A-Za-z0-9-]+", text.lower()))


def keyword_search(query: str, *, top_k: int = 10) -> list[dict[str, Any]]:
    query_tokens = tokenize(query)
    results = []
    for document in list_documents(collection=COLLECTION):
        common = query_tokens & tokenize(document["content"])
        if common:
            results.append({**document, "score": len(common) / max(len(query_tokens), 1)})
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


def reciprocal_rank_fusion(
    result_groups: list[list[dict[str, Any]]],
    *,
    top_k: int = 3,
    rank_constant: int = 60,
) -> list[dict[str, Any]]:
    """서로 단위가 다른 점수 대신 각 검색기의 순위를 결합합니다."""
    fused: dict[str, dict[str, Any]] = {}
    for results in result_groups:
        for rank, item in enumerate(results, start=1):
            document_id = item["id"]
            if document_id not in fused:
                fused[document_id] = {**item, "rrf_score": 0.0, "matched_by": 0}
            fused[document_id]["rrf_score"] += 1 / (rank_constant + rank)
            fused[document_id]["matched_by"] += 1
    return sorted(fused.values(), key=lambda item: item["rrf_score"], reverse=True)[:top_k]


def hybrid_search(query: str, *, top_k: int = 3) -> dict[str, list[dict[str, Any]]]:
    keyword_results = keyword_search(query, top_k=10)
    vector_results = similarity_search(query, collection=COLLECTION, top_k=10)
    return {
        "keyword": keyword_results,
        "vector": vector_results,
        "hybrid": reciprocal_rank_fusion([keyword_results, vector_results], top_k=top_k),
    }


def prepare_documents() -> None:
    delete_collection(COLLECTION)
    for index, (content, source) in enumerate(DOCUMENTS):
        upsert_text(
            collection=COLLECTION,
            title="객실 정책",
            content=content,
            source=source,
            chunk_index=index,
            metadata={"category": "hotel"},
        )


if __name__ == "__main__":
    prepare_documents()
    question = "A-1703에 강아지와 묵으면 비용이 더 드나요?"
    print("질문:", question)
    for mode, results in hybrid_search(question).items():
        print(f"\n[{mode}]")
        for item in results:
            score = item.get("rrf_score", item["score"])
            print(f"{score:.4f} | {item['source']} | {item['content']}")
