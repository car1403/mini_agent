import streamlit as st

from clients.agent_client import get_rag_status, index_rag_documents
from core.api_client import BackendAPIError


st.title("5️⃣ Ollama + pgvector")
st.caption("같은 RAG 흐름에서 검색 구현만 실제 Embedding과 Vector DB로 교체합니다.")

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

st.info("색인이 끝나면 '문서 검색' 또는 '근거 기반 답변' 메뉴에서 pgvector를 선택하세요.")
