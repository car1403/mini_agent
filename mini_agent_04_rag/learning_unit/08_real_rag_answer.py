"""pgvector 검색 Context를 실제 LLM에 전달하고 근거 답변과 출처를 확인합니다."""

import httpx
from _rag_backend import PROVIDER, print_help, request

if __name__ == "__main__":
    try:
        result = request("POST", "/api/rag/answer", {
            "query": "호텔을 당일 취소하면 환불받을 수 있나요?",
            "mode": "pgvector", "top_k": 3, "provider": PROVIDER, "use_cache": False,
        })
        # 답변뿐 아니라 LLM에 전달된 Context와 출처를 함께 검증합니다.
        print("답변:", result["answer"])
        print("출처:", result["sources"])
        print("Context:\n", result["context"])
        print("Trace:", result["trace"])
    except httpx.HTTPError as error:
        print_help(error)
