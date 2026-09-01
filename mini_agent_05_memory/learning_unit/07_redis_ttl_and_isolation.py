"""07. Backend를 통해 Redis 사용자 격리와 Sliding TTL을 확인합니다.

학습 목표:
- 같은 session_id도 user_id에 따라 별도 상태가 되는지 확인합니다.
- 조회할 때 TTL을 다시 늘리는 Sliding TTL 동작을 관찰합니다.

실행: python .\07_redis_ttl_and_isolation.py
외부 서비스: Mini Agent 05 Backend와 Redis 필요
"""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        print("[07] Redis TTL과 사용자 격리\n")
        for user, city in (("user-a", "부산"), ("user-b", "제주")):
            request("POST", "/api/memory/sessions", {
                "user_id": user, "session_id": "trip", "state": {"city": city},
            })
        # session_id가 같아도 user_id가 다르면 서로 다른 Redis Key를 조회합니다.
        print("A:", request("GET", "/api/memory/sessions/trip?user_id=user-a"))
        print("B:", request("GET", "/api/memory/sessions/trip?user_id=user-b"))
        print("TTL 연장:", request("GET", "/api/memory/sessions/trip?user_id=user-a&refresh_ttl=true"))
        print("\n핵심: Redisㅁ Session Key는 사용자와 Session을 모두 구분해야 합니다.")
    except httpx.HTTPError as error:
        print_help(error)
