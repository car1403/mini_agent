import streamlit as st

from api_client import make_chunks, search_documents


st.title("1. Chunk와 키워드 검색")
text = st.text_area(
    "문서",
    "체크인 3일 전까지 취소하면 전액 환불합니다. 체크인 당일에는 환불하지 않습니다.",
)
chunk_size = st.slider("Chunk에 포함할 문장 수", 1, 3, 1)

if st.button("Chunk 만들기"):
    try:
        st.json(make_chunks(text, chunk_size))
    except RuntimeError as error:
        st.error(str(error))

st.divider()
question = st.text_input("검색 질문", "호텔 당일 취소 환불")
if st.button("키워드 검색"):
    try:
        result = search_documents(question, "keyword", 3)
        st.json(result["results"])
    except RuntimeError as error:
        st.error(str(error))
