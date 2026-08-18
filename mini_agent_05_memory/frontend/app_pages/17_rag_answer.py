import streamlit as st

from clients.agent_client import answer_with_rag
from core.api_client import BackendAPIError


st.title("4️⃣ 근거 기반 답변")
st.caption("검색 결과로 Context를 만들고, 근거가 없으면 답변을 제한합니다.")

query = st.text_input("질문", "호텔을 당일 취소하면 어떻게 되나요?")
mode = st.radio("검색 방식", ["keyword", "pgvector"], horizontal=True)
provider = st.selectbox("답변 Provider", ["mock", "gemini", "openai", "ollama"])
top_k = st.slider("Context에 포함할 문서 수", 1, 5, 3)

if st.button("RAG 답변 만들기", type="primary"):
    try:
        result = answer_with_rag(query, mode, top_k, provider)
        if result["grounded"]:
            st.success(result["answer"])
        else:
            st.warning(result["answer"])
        st.write("출처", result["sources"] or "없음")
        with st.expander("LLM에 전달한 Context"):
            st.code(result["context"] or "Context 없음", language="text")
        with st.expander("검색 결과"):
            st.json(result["results"])
    except BackendAPIError as error:
        st.error(str(error))
