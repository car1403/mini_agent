"""문장을 직접 입력해 pgvector에 저장하고 의미가 비슷한 문장을 검색합니다."""

from _pgvector_store import delete_collection, similarity_search, upsert_text


COLLECTION = "rag_text_lesson"
SENTENCES = [
    "반려동물 동반 객실은 1박당 3만 원이 추가됩니다.",
    "조식은 오전 7시부터 10시까지 1층 식당에서 제공합니다.",
    "체크아웃 시간을 오후 2시까지 연장하면 2만 원이 부과됩니다.",
]


if __name__ == "__main__":
    delete_collection(COLLECTION)
    for index, sentence in enumerate(SENTENCES):
        document_id = upsert_text(
            collection=COLLECTION,
            title=f"직접 입력 문장 {index + 1}",
            content=sentence,
            source="manual-input",
            chunk_index=index,
            metadata={"category": "hotel", "input_type": "text"},
        )
        print("저장:", document_id, sentence)

    query = "강아지와 함께 숙박하면 비용이 더 드나요?"
    print("\n질문:", query)
    for item in similarity_search(query, collection=COLLECTION, top_k=3):
        print(f"{item['score']:.3f} | {item['content']}")
