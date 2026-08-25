import streamlit as st

from clients.agent_client import get_rag_documents
from core.api_client import BackendAPIError


st.title("1️⃣ RAG 흐름")
st.info("RAG는 먼저 관련 문서를 찾고, 찾은 근거와 함께 LLM에게 질문합니다.")

st.code("질문 → 검색 → Context 구성 → LLM 답변 → 출처 표시", language="text")

left, right = st.columns(2)
with left:
    st.subheader("LLM만 사용")
    st.write("학습 시점 이후의 사내 정책이나 수업용 문서를 알 수 없습니다.")
with right:
    st.subheader("RAG 사용")
    st.write("외부 문서를 검색하므로 어떤 문서를 근거로 답했는지 보여줄 수 있습니다.")

st.subheader("이번 실습 문서")
try:
    for document in get_rag_documents()["documents"]:
        with st.expander(f"{document['title']} · {document['source']}"):
            st.write(document["content"])
except BackendAPIError as error:
    st.error(str(error))
