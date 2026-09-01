"""09. Backend를 통해 PostgreSQL upsert와 사용자 격리를 확인합니다.

학습 목표:
- 같은 사용자와 key를 다시 저장하면 기존 행이 수정되는지 확인합니다.
- 다른 사용자의 조회 결과에 내 Memory가 섞이지 않는지 확인합니다.

실행: python .\09_postgres_upsert_and_isolation.py
외부 서비스: Mini Agent 05 Backend와 PostgreSQL 필요
"""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        print("[09] PostgreSQL upsert와 사용자 격리\n")
        base = {"user_id": "user-a", "key": "hotel_preference", "storage": "postgres"}
        first = request("POST", "/api/memory/items", {**base, "value": "조용한 호텔"})
        second = request("POST", "/api/memory/items", {**base, "value": "조용하고 금연인 호텔"})
        # (user_id, memory_key) 충돌 시 같은 ID의 값만 갱신됩니다.
        print("같은 ID:", first["id"] == second["id"])
        print("user-a:", request("GET", "/api/memory/items/user-a?storage=postgres"))
        print("user-b:", request("GET", "/api/memory/items/user-b?storage=postgres"))
        print("\n핵심: 장기 Memory의 고유 범위는 user_id와 memory key의 조합입니다.")
    except httpx.HTTPError as error:
        print_help(error)
