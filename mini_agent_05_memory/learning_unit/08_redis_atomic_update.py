"""08. Redis WATCH/MULTI와 version으로 동시 갱신 충돌을 방지합니다.

학습 목표:
- 두 요청이 같은 이전 version을 수정할 때 생기는 덮어쓰기를 이해합니다.
- 오래된 version의 요청이 HTTP 409로 거부되는지 확인합니다.

실행: python .\08_redis_atomic_update.py
외부 서비스: Mini Agent 05 Backend와 Redis 필요
"""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        print("[08] Redis 원자 갱신\n")
        request("POST", "/api/memory/sessions", {
            "user_id": "user-a", "session_id": "atomic", "state": {"city": "부산"},
        })
        updated = request("PATCH", "/api/memory/sessions", {
            "user_id": "user-a", "session_id": "atomic",
            "changes": {"guests": 2}, "expected_version": 0,
        })
        print("정상 갱신:", updated)
        # 같은 version으로 다시 쓰면 HTTP 409가 되어 최신 상태를 덮어쓰지 않습니다.
        request("PATCH", "/api/memory/sessions", {
            "user_id": "user-a", "session_id": "atomic",
            "changes": {"guests": 4}, "expected_version": 0,
        })
    except httpx.HTTPStatusError as error:
        print("예상한 충돌:", error.response.status_code, error.response.text)
        print("\n핵심: version이 맞는 요청만 저장해 최신 Session의 덮어쓰기를 막습니다.")
    except httpx.HTTPError as error:
        print_help(error)
