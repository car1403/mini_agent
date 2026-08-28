import json

import streamlit as st

from api_client import answer_question, search_documents


st.title("5. Cache와 검색 조건")
st.subheader("동일 질문 Cache")
question = st.text_input("질문", "수하물은 몇 kg까지 가능한가요?")
if st.button("질문 보내기"):
    try:
        result = answer_question(question, "pgvector", 3, True, True)
        status = "HIT" if result["cache_hit"] else "MISS 후 저장"
        st.info(f"Redis Cache: {status}")
        st.write(result["answer"])
    except RuntimeError as error:
        st.error(str(error))

st.divider()
st.subheader("Metadata와 Hybrid 검색")
filter_text = st.text_input("Metadata JSON", "{}")
if st.button("Hybrid 검색"):
    try:
        metadata = json.loads(filter_text)
        result = search_documents(question, "hybrid", 3, None, metadata)
        st.json(result["results"])
    except (RuntimeError, json.JSONDecodeError) as error:
        st.error(str(error))
