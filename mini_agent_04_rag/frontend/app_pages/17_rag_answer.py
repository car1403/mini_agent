import streamlit as st

from clients.agent_client import answer_with_rag
from core.api_client import BackendAPIError


st.title("4️⃣ 근거 기반 답변")
st.caption("검색 결과로 Context를 만들고, 근거가 없으면 답변을 제한합니다.")

query = st.text_input("질문", "호텔을 당일 취소하면 어떻게 되나요?")
mode = st.radio("검색 방식", ["keyword", "pgvector"], horizontal=True)
provider = st.selectbox("답변 Provider", ["mock", "gemini", "openai", "ollama"])
top_k = st.slider("Context에 포함할 문서 수", 1, 5, 3)
use_cache = st.checkbox("Redis 답변 Cache 사용", value=True)

if st.button("RAG 답변 만들기", type="primary"):
    try:
        result = answer_with_rag(query, mode, top_k, provider, use_cache)
        if result["grounded"]:
            st.success(result["answer"])
        else:
            st.warning(result["answer"])
        st.write("출처", result["sources"] or "없음")
        if result["cache_hit"]:
            st.info(f"Redis Cache HIT · 남은 TTL {result['cache_ttl_seconds']}초")
        elif use_cache:
            st.caption("Redis Cache MISS · 새 검색/답변 결과를 Cache에 저장했습니다.")
        with st.expander("LLM에 전달한 Context"):
            st.code(result["context"] or "Context 없음", language="text")
        with st.expander("검색 결과"):
            st.json(result["results"])
        with st.expander("전체 RAG Trace", expanded=True):
            st.json(result["trace"])
    except BackendAPIError as error:
        st.error(str(error))
