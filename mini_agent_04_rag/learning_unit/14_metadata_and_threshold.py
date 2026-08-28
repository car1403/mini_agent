"""Metadata Filter와 유사도 임계값으로 검색 범위와 품질을 제어합니다."""

from _pgvector_store import delete_collection, similarity_search, upsert_text


COLLECTION = "rag_filter_lesson"
DOCUMENTS = [
    ("호텔", "호텔 예약은 체크인 3일 전까지 취소하면 전액 환불합니다.", "hotel", "active"),
    ("항공", "국내선 항공권은 출발 7일 전까지 취소 수수료가 없습니다.", "flight", "active"),
    ("이전 호텔 정책", "호텔 예약은 당일에도 전액 환불합니다.", "hotel", "expired"),
]


def prepare_documents() -> None:
    delete_collection(COLLECTION)
    for index, (title, content, category, status) in enumerate(DOCUMENTS):
        upsert_text(
            collection=COLLECTION,
            title=title,
            content=content,
            source=f"{category}-policy.md",
            chunk_index=index,
            metadata={"category": category, "status": status, "language": "ko"},
        )


def print_results(label: str, results: list[dict]) -> None:
    print(f"\n[{label}]")
    if not results:
        print("조건을 만족하는 검색 결과가 없습니다.")
    for item in results:
        print(f"{item['score']:.3f} | {item['metadata']} | {item['content']}")


if __name__ == "__main__":
    prepare_documents()
    question = "예약을 취소하면 돈을 모두 돌려받을 수 있나요?"

    print_results(
        "Filter 없음",
        similarity_search(question, collection=COLLECTION, top_k=3),
    )
    print_results(
        "현재 사용 중인 호텔 정책만",
        similarity_search(
            question,
            collection=COLLECTION,
            top_k=3,
            metadata_filter={"category": "hotel", "status": "active"},
        ),
    )
    print_results(
        "현재 호텔 정책 + 높은 임계값",
        similarity_search(
            question,
            collection=COLLECTION,
            top_k=3,
            score_threshold=0.75,
            metadata_filter={"category": "hotel", "status": "active"},
        ),
    )
