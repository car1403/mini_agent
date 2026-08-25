import streamlit as st

from clients.agent_client import get_rag_status, index_rag_documents
from core.api_client import BackendAPIError


st.title("5️⃣ Ollama + pgvector + Redis")
st.caption("pgvector는 영구 의미 검색을, Redis는 TTL 답변 Cache를 담당합니다.")

st.code(
    "docker compose up -d\n"
    "docker exec mini-agent-ollama ollama pull embeddinggemma",
    language="powershell",
)

if st.button("연결 상태 확인"):
    try:
        st.json(get_rag_status())
    except BackendAPIError as error:
        st.error(str(error))

st.warning("색인은 Mini Agent 전용 collection만 초기화합니다. 다른 단계의 문서는 삭제하지 않습니다.")
if st.button("교육용 문서 색인", type="primary"):
    try:
        result = index_rag_documents(reset_collection=True)
        st.success(f"{result['indexed_count']}개 Chunk 색인 완료")
        st.json(result)
    except BackendAPIError as error:
        st.error(str(error))

st.info("색인이 끝나면 pgvector 검색을 실행하고 같은 질문을 두 번 보내 Redis MISS→HIT를 비교하세요.")
