"""동일한 RAG 질문을 두 번 보내 Redis Cache MISS와 HIT를 관찰합니다."""

import httpx
from _rag_backend import PROVIDER, print_help, request

PAYLOAD = {
    "query": "위탁 수하물은 몇 kg까지 가능한가요?", "mode": "pgvector",
    "top_k": 2, "provider": PROVIDER, "use_cache": True,
}

if __name__ == "__main__":
    try:
        # 재색인은 기존 RAG Cache를 무효화하므로 첫 호출이 MISS임을 재현할 수 있습니다.
        request("POST", "/api/rag/index", {"reset_collection": False})
        # 같은 조건의 두 번째 호출은 Redis에서 답변을 읽고 남은 TTL을 반환합니다.
        first = request("POST", "/api/rag/answer", PAYLOAD)
        second = request("POST", "/api/rag/answer", PAYLOAD)
        print("1회차:", {"cache_hit": first["cache_hit"], "trace": first["trace"]})
        print("2회차:", {"cache_hit": second["cache_hit"], "ttl": second["cache_ttl_seconds"], "trace": second["trace"]})
    except httpx.HTTPError as error:
        print_help(error)
