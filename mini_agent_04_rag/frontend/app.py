import streamlit as st


st.set_page_config(
    page_title="Mini Agent 04 · RAG",
    page_icon="📚",
    layout="wide",
)

pages = [
    st.Page("simple_pages/01_home.py", title="HOME", default=True),
    st.Page("simple_pages/02_chunk_search.py", title="1. Chunk와 키워드 검색"),
    st.Page("simple_pages/03_vector_search.py", title="2. pgvector 의미 검색"),
    st.Page("simple_pages/04_rag_answer.py", title="3. 근거 기반 답변"),
    st.Page("simple_pages/05_pdf_rag.py", title="4. PDF RAG"),
    st.Page("simple_pages/06_cache_filter.py", title="5. Cache와 검색 조건"),
]

st.navigation(pages).run()
