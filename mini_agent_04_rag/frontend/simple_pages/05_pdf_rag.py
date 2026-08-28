import streamlit as st

from api_client import answer_question, upload_pdf


st.title("4. PDF RAG")
pdf = st.file_uploader("텍스트형 PDF", type=["pdf"])

if st.button("PDF 저장", disabled=pdf is None):
    try:
        st.json(upload_pdf(pdf.name, pdf.getvalue()))
    except RuntimeError as error:
        st.error(str(error))

question = st.text_input("PDF 질문", "당일 취소 규정은 어떻게 되나요?")
if st.button("PDF에서 답변 찾기"):
    try:
        result = answer_question(question, "pgvector", 3, True, False)
        st.success(result["answer"])
        st.write("출처", result["sources"] or "없음")
    except RuntimeError as error:
        st.error(str(error))
