"""실제 pgvector를 사용하는 RAG Lab 03~05 통합 화면입니다."""

import streamlit as st

from clients.agent_client import (
    get_indexed_rag_source, index_rag_pdf, search_rag,
    search_rag_lab_policies, search_rag_lab_products,
    seed_rag_lab_policies, seed_rag_lab_products,
)
from core.api_client import BackendAPIError


st.title("🧪 RAG Labs 03~05")
st.caption("상품 조건 검색 · Backend ACL · PDF 페이지 출처를 실제 pgvector에서 확인합니다.")

product_tab, acl_tab, pdf_tab = st.tabs([
    "03 · 쇼핑몰 상품 검색", "04 · 사내 규정 ACL", "05 · PDF 여행 가이드",
])

with product_tab:
    st.subheader("Metadata·가격·Hybrid Search")
    if st.button("교육용 상품 Catalog 색인", use_container_width=True):
        try:
            result = seed_rag_lab_products()
            st.success("상품 Catalog를 pgvector에 색인했습니다.")
            st.json(result)
        except BackendAPIError as error:
            st.error(str(error))

    product_query = st.text_input("상품 질문", "10만원 이하 가벼운 장거리 달리기 신발")
    product_category = st.selectbox("category", ["shoes", "bag", "전체"])
    use_max_price = st.checkbox("최대 가격 적용", value=True)
    max_price = st.number_input("max_price", min_value=0, value=100000, step=10000)
    if st.button("상품 Hybrid 검색", type="primary", use_container_width=True):
        try:
            result = search_rag_lab_products(
                product_query,
                None if product_category == "전체" else product_category,
                int(max_price) if use_max_price else None,
            )
            st.caption(f"Hybrid 후보 {result['candidate_count']}개에서 조건 적용")
            for item in result["results"]:
                metadata = item["metadata"]
                st.markdown(f"**{metadata['sku']} · {metadata['price']:,}원**")
                st.write(item["content"])
                st.caption(f"category={metadata['category']} · RRF={item['score']:.6f}")
        except BackendAPIError as error:
            st.error(str(error))

with acl_tab:
    st.subheader("인증 역할 기반 사내 규정 검색")
    st.info("역할은 JSON Body가 아니라 X-Demo-Role Header로 전달되고 Backend가 ACL Filter를 강제합니다.")
    if st.button("교육용 사내 규정 색인", use_container_width=True):
        try:
            result = seed_rag_lab_policies()
            st.success("역할별 사내 규정을 pgvector에 색인했습니다.")
            st.json(result)
        except BackendAPIError as error:
            st.error(str(error))

    policy_query = st.text_input("규정 질문", "급여 정정은 누가 승인하나요?")
    role = st.selectbox("인증된 Demo 역할", ["employee", "manager", "hr"])
    if st.button("ACL 검색", type="primary", use_container_width=True):
        try:
            result = search_rag_lab_policies(policy_query, role)
            if not result["results"]:
                st.warning("현재 역할로 조회할 수 있는 근거가 없습니다.")
            for item in result["results"]:
                st.write(item["content"])
                st.caption(f"허용 역할: {item['metadata']['allowed_roles']}")
            st.code(result["termination_reason"])
        except BackendAPIError as error:
            st.error(str(error))

with pdf_tab:
    st.subheader("PDF Chunking·페이지 출처·중복 색인")
    uploaded = st.file_uploader("텍스트형 여행 가이드 PDF", type=["pdf"], key="rag_lab_05_pdf")
    pdf_title = st.text_input("PDF 제목", "여행 가이드", key="rag_lab_05_title")
    pdf_query = st.text_input("PDF 질문", "추천 관광지는 어디인가요?", key="rag_lab_05_query")
    if st.button("PDF 색인·검색", type="primary", disabled=uploaded is None, use_container_width=True):
        try:
            indexed = index_rag_pdf(uploaded.name, uploaded.getvalue(), pdf_title)
            source_id = indexed["source"]
            stored = get_indexed_rag_source(source_id)
            searched = search_rag(
                pdf_query, "pgvector", 3, None,
                {"input_type": "pdf", "source_id": source_id},
            )
            st.json({"index": indexed, "stored_chunk_count": stored["count"]})
            for item in searched["results"]:
                page = item["metadata"].get("page_number", "?")
                st.markdown(f"**{item['source']} · p.{page} · score {item['score']:.3f}**")
                st.write(item["content"])
            with st.expander("실제 저장 Chunk"):
                st.json(stored["chunks"])
        except BackendAPIError as error:
            st.error(str(error))
