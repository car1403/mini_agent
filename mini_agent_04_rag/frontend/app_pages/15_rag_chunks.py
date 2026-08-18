import streamlit as st

from clients.agent_client import preview_chunks
from core.api_client import BackendAPIError


st.title("2️⃣ 문서와 Chunk")
st.caption("긴 문서를 검색하기 좋은 작은 단위로 나누고 출처 정보를 붙입니다.")

text = st.text_area(
    "문서",
    "체크인 3일 전까지 취소하면 전액 환불합니다. 체크인 2일 전에는 50%를 환불합니다. 체크인 당일에는 환불하지 않습니다. 예약 변경은 고객센터에서 처리합니다.",
    height=150,
)
source = st.text_input("source", "hotel-refund.md")
title = st.text_input("title", "호텔 환불 정책")
sentences_per_chunk = st.slider("Chunk 하나에 넣을 문장 수", 1, 4, 2)

if st.button("Chunk 나누기", type="primary"):
    try:
        result = preview_chunks(text, source, title, sentences_per_chunk)
        st.success(f"{result['count']}개의 Chunk를 만들었습니다.")
        for chunk in result["chunks"]:
            with st.expander(chunk["chunk_id"]):
                st.write(chunk["text"])
                st.json({"source": chunk["source"], "title": chunk["title"], "chunk_index": chunk["chunk_index"]})
    except BackendAPIError as error:
        st.error(str(error))
