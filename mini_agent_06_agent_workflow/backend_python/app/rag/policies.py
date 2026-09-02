import re


POLICIES = [
    {
        "title": "숙소 취소",
        "content": "체크인 3일 전까지 취소하면 전액 환불됩니다.",
        "source": "hotel-refund.md",
    },
    {
        "title": "당일 취소",
        "content": "체크인 당일 취소는 숙박 요금의 100%가 부과됩니다.",
        "source": "hotel-refund.md",
    },
    {
        "title": "수하물",
        "content": "교육용 국내선 위탁 수하물 기본 허용량은 15kg입니다.",
        "source": "baggage.md",
    },
    {
        "title": "관광지 휴관",
        "content": "바다 박물관은 매주 월요일 휴관합니다.",
        "source": "attraction-hours.md",
    },
]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))


def search(query: str, limit: int = 3) -> list[dict]:
    query_tokens = _tokens(query)
    results = []
    for policy in POLICIES:
        score = len(query_tokens & _tokens(policy["title"] + " " + policy["content"])) / max(
            len(query_tokens), 1
        )
        if score > 0:
            results.append({**policy, "score": round(score, 3)})
    return sorted(results, key=lambda item: item["score"], reverse=True)[:limit]
