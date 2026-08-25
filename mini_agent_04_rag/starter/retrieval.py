DOCUMENTS = [
    {"text": "체크인 3일 전까지 취소하면 전액 환불합니다.", "source": "hotel-refund.md"},
    {"text": "위탁 수하물은 15kg까지 허용합니다.", "source": "baggage.md"},
]


def search(query: str) -> list[dict]:
    """TODO: query와 문서에서 겹치는 단어를 이용해 관련 문서를 반환하세요."""
    raise NotImplementedError


if __name__ == "__main__":
    print(search("호텔을 취소하면 환불되나요?"))
