# Solution 안내

| 학습 항목 | 완성 코드 |
| --- | --- |
| Chunk와 Metadata | `backend/app/rag/chunking.py` |
| 키워드 검색 | `backend/app/rag/keyword_store.py` |
| Ollama Embedding | `backend/app/rag/embedding.py` |
| pgvector 저장·검색 | `backend/app/rag/pgvector_store.py` |
| Redis TTL Cache | `backend/app/rag/redis_cache.py` |
| 근거 기반 답변 | `backend/app/rag/service.py` |
| FastAPI 연결 | `backend/app/routers/rag_router.py` |
| Streamlit Tool Loop | `frontend/app_pages/13_tool_loop.py` |
| Streamlit RAG·Trace·Cache | `frontend/app_pages/14~19` |

시간이 부족하면 `learning_unit` 01~05 후 완성 화면으로 넘어가고, 07~10에서 실제 검색·LLM·Cache Trace를 시연합니다.
