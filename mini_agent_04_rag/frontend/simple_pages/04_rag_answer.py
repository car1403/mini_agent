import streamlit as st

from api_client import answer_question


st.title("3. 근거 기반 답변")
question = st.text_input("질문", "호텔을 당일 취소하면 환불되나요?")
mode = st.radio("검색 방식", ["keyword", "pgvector"], horizontal=True)
use_ollama = st.checkbox("Ollama로 답변 생성")

if st.button("RAG 답변 만들기", type="primary"):
    try:
        result = answer_question(question, mode, 3, use_ollama, False)
        st.success(result["answer"])
        st.write("출처", result["sources"] or "없음")
        with st.expander("검색 결과"):
            st.json(result["results"])
        with st.expander("Ollama에 전달한 Context"):
            st.code(result["context"] or "Context 없음")
    except RuntimeError as error:
        st.error(str(error))
