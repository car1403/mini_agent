"""실제 pgvector에서 Keyword·Vector·Hybrid의 Hit@K와 MRR을 비교합니다."""

import re
import sys
from pathlib import Path
from typing import Any


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _pgvector_store import delete_collection, list_documents, similarity_search, upsert_text


COLLECTION = "rag_retrieval_evaluation_lab"
DOCUMENTS = [
    ("refund", "체크인 당일 취소에는 숙박 요금 전액이 부과됩니다."),
    ("baggage", "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다."),
    ("museum", "바다 박물관은 매주 화요일에 휴관합니다."),
    ("pet", "반려동물 동반 객실은 1박당 3만 원이 추가됩니다."),
]
EVALUATION_SET = [
    ("숙소를 예약 당일 취소하면 돈을 돌려받나요?", "refund"),
    ("비행기에 맡길 수 있는 가방 무게는?", "baggage"),
    ("바다 박물관이 쉬는 요일은?", "museum"),
    ("강아지와 숙박할 때 추가 비용이 있나요?", "pet"),
]


def prepare_documents() -> None:
    delete_collection(COLLECTION)
    for index, (document_id, content) in enumerate(DOCUMENTS):
        upsert_text(
            collection=COLLECTION,
            title=document_id,
            content=content,
            source=f"{document_id}.md",
            chunk_index=index,
            metadata={"evaluation_id": document_id},
        )


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))


def keyword_search(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    query_tokens = tokens(query)
    results = []
    for item in list_documents(collection=COLLECTION):
        common = query_tokens & tokens(item["content"])
        if common:
            results.append({**item, "score": len(common) / max(len(query_tokens), 1)})
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


def fuse(keyword: list[dict[str, Any]], vector: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
    fused: dict[str, dict[str, Any]] = {}
    for group in (keyword, vector):
        for rank, item in enumerate(group, start=1):
            current = fused.setdefault(item["id"], {**item, "rrf_score": 0.0})
            current["rrf_score"] += 1 / (60 + rank)
    return sorted(fused.values(), key=lambda item: item["rrf_score"], reverse=True)[:top_k]


def evaluate(mode: str, *, top_k: int = 3) -> dict[str, Any]:
    reciprocal_ranks = []
    hits = 0
    cases = []
    for question, expected_id in EVALUATION_SET:
        keyword = keyword_search(question, top_k)
        vector = similarity_search(question, collection=COLLECTION, top_k=top_k)
        results = {"keyword": keyword, "vector": vector, "hybrid": fuse(keyword, vector, top_k)}[mode]
        ranked_ids = [item["metadata"]["evaluation_id"] for item in results]
        rank = ranked_ids.index(expected_id) + 1 if expected_id in ranked_ids else None
        hits += int(rank is not None)
        reciprocal_ranks.append(1 / rank if rank else 0.0)
        cases.append({"question": question, "expected": expected_id, "ranked": ranked_ids, "rank": rank})
    return {
        "mode": mode,
        f"hit@{top_k}": hits / len(EVALUATION_SET),
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks),
        "cases": cases,
    }


if __name__ == "__main__":
    prepare_documents()
    for search_mode in ("keyword", "vector", "hybrid"):
        report = evaluate(search_mode, top_k=3)
        print(f"\n[{search_mode}] Hit@3={report['hit@3']:.3f}, MRR={report['mrr']:.3f}")
        for case in report["cases"]:
            print(case)

