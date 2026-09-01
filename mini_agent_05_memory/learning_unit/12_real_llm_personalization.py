"""12. 관련 있는 PostgreSQL Memory만 사용해 LLM 답변을 개인화합니다.

학습 목표:
- 저장된 전체 Memory와 실제 답변에 사용한 Memory를 구분합니다.
- Trace에서 Memory 선택과 LLM 호출 과정을 관찰합니다.

실행: python .\12_real_llm_personalization.py
외부 서비스: Mini Agent 05 Backend, PostgreSQL과 선택한 LLM Provider 필요
"""

import httpx
from _memory_backend import PROVIDER, print_help, request

if __name__ == "__main__":
    try:
        print("[12] 실제 LLM Memory 개인화\n")
        result = request("POST", "/api/memory/personalize", {
            "user_id": "user-a", "question": "호텔을 추천해 줘",
            "storage": "postgres", "provider": PROVIDER,
        })
        print("사용 Memory:", result["used_memories"])
        print("답변:", result["answer"])
        print("Trace:", result["trace"])
        print("\n핵심: LLM에는 저장된 전체 정보가 아니라 질문에 필요한 Memory만 전달합니다.")
    except httpx.HTTPError as error:
        print_help(error)
