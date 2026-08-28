"""키워드가 겹치는 정도로 관련 Chunk를 찾습니다."""

from dataclasses import dataclass
import re


@dataclass
class Chunk:
    text: str
    source: str


CHUNKS = [
    Chunk("체크인 3일 전까지 취소하면 전액 환불합니다.", "hotel-refund.md"),
    Chunk("체크인 당일 취소에는 숙박 요금 전액이 부과됩니다.", "hotel-refund.md"),
    Chunk("교육용 국내선의 위탁 수하물은 15kg까지 허용합니다.", "baggage.md"),
    Chunk("바다 박물관은 매주 화요일에 휴관합니다.", "attraction-hours.md"),
]


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))


def search(query: str, top_k: int = 2) -> list[dict]:
    query_tokens = tokenize(query)
    results = []
    for chunk in CHUNKS:
        common = query_tokens & tokenize(chunk.text)
        score = len(common) / max(len(query_tokens), 1)
        if score > 0:
            results.append({"text": chunk.text, "source": chunk.source, "score": round(score, 3)})
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in search("호텔을 당일 취소하면 환불되나요?"):
        print(result)
