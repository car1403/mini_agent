"""검색 결과로 Context를 만들고 근거가 없으면 답변을 제한합니다."""

DOCUMENTS = [
    {"text": "체크인 3일 전까지 취소하면 전액 환불합니다.", "source": "hotel-refund.md"},
    {"text": "체크인 당일 취소에는 숙박 요금 전액이 부과됩니다.", "source": "hotel-refund.md"},
    {"text": "교육용 국내선의 위탁 수하물은 15kg까지 허용합니다.", "source": "baggage.md"},
]


def search(question: str) -> list[dict]:
    if "당일" in question and ("취소" in question or "환불" in question):
        return [DOCUMENTS[1]]
    if "취소" in question or "환불" in question:
        return [DOCUMENTS[0]]
    if "수하물" in question or "짐" in question:
        return [DOCUMENTS[2]]
    return []


def answer(question: str) -> dict:
    documents = search(question)
    if not documents:
        return {
            "answer": "제공된 여행 정책 문서에서 근거를 찾지 못했습니다.",
            "grounded": False,
            "context": "",
            "sources": [],
        }
    context = "\n".join(f"[{item['source']}] {item['text']}" for item in documents)
    return {
        "answer": documents[0]["text"],
        "grounded": True,
        "context": context,
        "sources": sorted({item["source"] for item in documents}),
    }


if __name__ == "__main__":
    print(answer("호텔을 당일 취소하면 어떻게 되나요?"))
    print(answer("여권을 잃어버리면 어떻게 하나요?"))
