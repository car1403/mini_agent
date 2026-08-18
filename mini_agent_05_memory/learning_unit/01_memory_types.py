"""대화 기록, 단기 상태, 장기 Memory, RAG 문서를 비교합니다."""

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
    for item in MEMORY_TYPES:
        print(item)

    print("\nMemory는 사용자나 대화의 상태이고, RAG는 외부 지식 문서를 검색합니다.")
