"""pgvector에 저장된 PDF Chunk를 질문과의 유사도로 검색합니다."""

from _pgvector_store import similarity_search


COLLECTION = "rag_pdf_lesson"
QUESTION = "당일 취소 규정은 어떻게 되나요?"
TOP_K = 3


def search_pdf(question: str) -> list[dict]:
    return similarity_search(
        question,
        collection=COLLECTION,
        top_k=TOP_K,
    )


if __name__ == "__main__":
    results = search_pdf(QUESTION)

    print(f"질문: {QUESTION}")
    if not results:
        print("관련 PDF Chunk를 찾지 못했습니다.")

    for rank, item in enumerate(results, start=1):
        page = item["metadata"].get("page_number", "?")
        print(f"\n{rank}위 · score={item['score']:.3f}")
        print(f"출처: {item['source']} · {page}페이지")
        print(f"내용: {item['content']}")
