"""RAG의 전체 흐름을 외부 패키지 없이 확인합니다."""

DOCUMENTS = [
    {"source": "hotel-refund.md", "text": "체크인 3일 전까지 취소하면 전액 환불합니다."},
    {"source": "baggage.md", "text": "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다."},
]


def llm_only_answer(question: str) -> str:
    return "제가 알고 있는 일반적인 내용으로는 정확한 정책을 확인하기 어렵습니다."


def retrieve(question: str) -> list[dict]:
    if "취소" in question or "환불" in question:
        return [DOCUMENTS[0]]
    if "수하물" in question or "짐" in question:
        return [DOCUMENTS[1]]
    return []


def rag_answer(question: str) -> dict:
    documents = retrieve(question)
    if not documents:
        return {"answer": "제공된 문서에서 근거를 찾지 못했습니다.", "sources": []}
    return {"answer": documents[0]["text"], "sources": [documents[0]["source"]]}


if __name__ == "__main__":
    question = "호텔을 취소하면 환불되나요?"
    print("1. LLM만 사용:", llm_only_answer(question))
    print("2. 문서 검색:", retrieve(question))
    print("3. RAG 답변:", rag_answer(question))
