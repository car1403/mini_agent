"""11. Redis 단기 상태와 PostgreSQL 장기 데이터를 함께 복원합니다.

학습 목표:
- 빠르게 만료되는 Session과 영구 데이터의 역할을 구분합니다.
- 저장소별 복원 결과와 오류가 Trace에 따로 기록되는지 확인합니다.

실행: python .\11_hybrid_session_restore.py
외부 서비스: Mini Agent 05 Backend, Redis와 PostgreSQL 필요
"""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        print("[11] Hybrid Memory 복원\n")
        request("POST", "/api/memory/sessions", {"user_id": "user-a", "session_id": "hybrid", "state": {"step": "hotel_search"}})
        request("POST", "/api/memory/items", {"user_id": "user-a", "key": "transportation", "value": "대중교통", "storage": "postgres"})
        # 각 저장소의 결과와 실패 여부가 trace에 별도로 기록됩니다.
        restored = request("GET", "/api/memory/restore/user-a/hybrid")
        print("Redis 단기 상태:", restored["session_state"])
        print("PostgreSQL 장기 Memory:", restored["long_term_memories"])
        print("최근 대화:", restored["recent_messages"])
        print("Trace:", restored["trace"])
        print("\n핵심: Hybrid 복원은 저장소를 합치되 각 데이터의 수명과 실패를 구분합니다.")
    except httpx.HTTPError as error:
        print_help(error)
