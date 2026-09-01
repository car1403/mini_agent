"""01. 대화 기록, 단기 상태, 장기 Memory, RAG 문서를 비교합니다.

학습 목표:
- 비슷해 보이는 네 가지 데이터의 목적과 보관 기간을 구분합니다.
- Memory와 RAG가 서로 다른 문제를 해결한다는 점을 이해합니다.

실행: python .\01_memory_types.py
외부 서비스: 필요 없음
"""

MEMORY_TYPES = [
    {
        "type": "conversation_history",
        "example": "사용자: 부산에 갈 거예요",
        "lifetime": "현재 대화",
        "storage": "메모리 또는 PostgreSQL",
    },
    {
        "type": "short_term_state",
        "example": "현재 단계: 숙소 정보 수집",
        "lifetime": "TTL까지",
        "storage": "Redis",
    },
    {
        "type": "long_term_memory",
        "example": "교통 선호: 대중교통",
        "lifetime": "사용자가 수정·삭제할 때까지",
        "storage": "PostgreSQL",
    },
    {
        "type": "rag_document",
        "example": "호텔 환불 정책",
        "lifetime": "문서가 갱신될 때까지",
        "storage": "PostgreSQL/pgvector",
    },
]


if __name__ == "__main__":
    print("[01] Memory와 RAG 데이터 종류\n")
    for item in MEMORY_TYPES:
        print(f"- {item['type']}")
        print(f"  예: {item['example']}")
        print(f"  보관 기간: {item['lifetime']}")
        print(f"  저장소: {item['storage']}")

    print("\n핵심: Memory는 사용자나 대화의 상태이고, RAG는 외부 지식 문서를 검색합니다.")
