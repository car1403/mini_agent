import streamlit as st

from clients.agent_client import index_rag_pdf, index_rag_text
from core.api_client import BackendAPIError


st.title("7️⃣ 텍스트·PDF 색인")
st.caption("직접 입력한 문장이나 텍스트형 PDF를 Chunk로 나누어 pgvector에 저장합니다.")

text_tab, pdf_tab = st.tabs(["직접 입력", "PDF 업로드"])
with text_tab:
    title = st.text_input("제목", "호텔 반려동물 정책")
    source = st.text_input("출처", "manual-hotel-policy.md")
    content = st.text_area("내용", "반려동물 동반 객실은 1박당 3만 원이 추가됩니다.")
    category = st.text_input("category", "hotel")
    status = st.selectbox("status", ["active", "expired"])
    if st.button("텍스트 색인", type="primary"):
        try:
            st.json(index_rag_text(title, content, source, {
                "category": category, "status": status, "language": "ko",
            }))
        except BackendAPIError as error:
            st.error(str(error))

with pdf_tab:
    uploaded = st.file_uploader("텍스트형 PDF", type=["pdf"])
    pdf_title = st.text_input("PDF 제목", "여행 정책 PDF")
    st.info("스캔 PDF는 OCR 처리 후 업로드해야 합니다. 결과에는 페이지 번호가 보존됩니다.")
    if st.button("PDF 색인", disabled=uploaded is None):
        try:
            st.json(index_rag_pdf(uploaded.name, uploaded.getvalue(), pdf_title))
        except BackendAPIError as error:
            st.error(str(error))
