"""13. 사용자가 자신의 Memory를 내보내고 전체 삭제하는 흐름을 확인합니다.

학습 목표:
- 사용자가 저장된 자신의 데이터를 확인할 수 있어야 함을 이해합니다.
- Redis Session, 장기 Memory와 대화 기록을 함께 삭제하는지 확인합니다.

실행: python .\13_memory_export_and_delete.py
외부 서비스: Mini Agent 05 Backend, Redis와 PostgreSQL 필요
주의: 예제 user-a의 데이터를 실제로 삭제합니다.
"""

import httpx
from _memory_backend import print_help, request

if __name__ == "__main__":
    try:
        print("[13] Memory 내보내기와 전체 삭제\n")
        print("삭제 전:", request("GET", "/api/memory/export/user-a"))
        print("삭제 결과:", request("DELETE", "/api/memory/users/user-a"))
        print("삭제 후:", request("GET", "/api/memory/export/user-a"))
        print("\n핵심: Memory 기능에는 저장뿐 아니라 확인·내보내기·삭제 권한도 필요합니다.")
    except httpx.HTTPError as error:
        print_help(error)
