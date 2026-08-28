import streamlit as st

from api_client import index_documents, search_documents


st.title("2. pgvector 의미 검색")
st.info("Ollama, embeddinggemma, PostgreSQL/pgvector가 필요합니다.")

if st.button("교육 문서 저장"):
    try:
        st.json(index_documents())
    except RuntimeError as error:
        st.error(str(error))

question = st.text_input("질문", "비행기에 짐을 몇 kg까지 실을 수 있나요?")
top_k = st.slider("가져올 결과 수", 1, 5, 3)
if st.button("의미 검색"):
    try:
        result = search_documents(question, "pgvector", top_k)
        st.json(result["results"])
    except RuntimeError as error:
        st.error(str(error))
