"""같은 질문의 키워드 검색과 실제 pgvector 의미 검색 결과를 비교합니다."""

import httpx
from _rag_backend import print_help, request

QUESTION = "숙소 예약을 취소하면 돈을 돌려받을 수 있나요?"

if __name__ == "__main__":
    try:
        # 실제 의미 검색을 위해 교육용 문서를 먼저 Ollama Embedding으로 색인합니다.
        print("색인:", request("POST", "/api/rag/index", {"reset_collection": True}))
        for mode in ("keyword", "pgvector"):
            result = request("POST", "/api/rag/search", {"query": QUESTION, "mode": mode, "top_k": 3})
            print(f"\n[{mode}]")
            for item in result["results"]:
                print(f"{item['score']:.3f} | {item['source']} | {item['content']}")
    except httpx.HTTPError as error:
        print_help(error)
