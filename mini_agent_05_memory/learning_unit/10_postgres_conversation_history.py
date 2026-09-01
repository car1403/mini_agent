"""10. PostgreSQL 대화를 사용자·Session별 최근 Window로 복원합니다.

학습 목표:
- 장기 선호와 대화 기록이 서로 다른 데이터임을 확인합니다.
- 대화 기록도 사용자와 Session 범위로 조회해야 함을 이해합니다.

실행: python .\10_postgres_conversation_history.py
외부 서비스: Mini Agent 05 Backend와 PostgreSQL 필요
"""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        print("[10] PostgreSQL 대화 기록\n")
        for role, content in (("user", "부산 여행을 준비 중이야."), ("assistant", "기간을 알려주세요."), ("user", "2박 3일이야.")):
            result = request("POST", "/api/memory/conversations", {
                "user_id": "user-a", "session_id": "trip-01", "role": role, "content": content,
            })
        print("최근 대화:", result["messages"])
        print("다른 사용자:", request("GET", "/api/memory/conversations/user-b/trip-01"))
        print("\n핵심: 복원할 대화는 인증된 사용자와 현재 Session 범위에서 최근 것만 조회합니다.")
    except httpx.HTTPError as error:
        print_help(error)
