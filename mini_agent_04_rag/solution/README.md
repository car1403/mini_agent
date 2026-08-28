# Solution 안내

| 학습 항목 | 완성 코드 |
| --- | --- |
| Chunk와 Metadata | `backend/app/rag/chunking.py` |
| 키워드 검색 | `backend/app/rag/keyword_store.py` |
| Ollama Embedding | `backend/app/rag/embedding.py` |
| pgvector 저장·검색 | `backend/app/rag/pgvector_store.py` |
| Redis TTL Cache | `backend/app/rag/redis_cache.py` |
| 근거 기반 답변 | `backend/app/simple_service.py` |
| FastAPI 연결 | `backend/app/simple_router.py` |
| Streamlit 화면 | `frontend/simple_pages` |

처음에는 `learning_unit` 01~05를 실행하고, 이후 Frontend의 1~5 화면에서 실제
pgvector·Ollama·Redis 흐름을 확인합니다.
