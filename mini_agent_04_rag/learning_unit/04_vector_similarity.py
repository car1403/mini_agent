"""작은 교육용 벡터로 의미 검색과 코사인 유사도를 관찰합니다."""

from math import sqrt


# 축의 의미: [환불, 수하물, 관광]
DOCUMENT_VECTORS = {
    "hotel-refund.md": [1.0, 0.0, 0.0],
    "baggage.md": [0.0, 1.0, 0.0],
    "attraction-hours.md": [0.0, 0.0, 1.0],
}


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_size = sqrt(sum(value * value for value in left))
    right_size = sqrt(sum(value * value for value in right))
    return dot / (left_size * right_size) if left_size and right_size else 0.0


if __name__ == "__main__":
    query_vector = [0.9, 0.1, 0.0]  # "숙소 예약을 취소하고 돈을 돌려받고 싶어요"
    scores = [
        (source, cosine_similarity(query_vector, vector))
        for source, vector in DOCUMENT_VECTORS.items()
    ]
    for source, score in sorted(scores, key=lambda item: item[1], reverse=True):
        print(f"{source}: {score:.3f}")
