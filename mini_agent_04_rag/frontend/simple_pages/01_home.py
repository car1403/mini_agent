import streamlit as st

from api_client import get_status


st.title("📚 Mini Agent 04 · RAG")
st.write("문서를 찾고, 찾은 내용을 근거로 답하는 과정을 단계별로 학습합니다.")
st.code("문서 → Chunk → Embedding → 검색 → Context → Ollama 답변", language="text")

if st.button("실행 환경 확인"):
    try:
        st.json(get_status())
    except RuntimeError as error:
        st.error(str(error))
