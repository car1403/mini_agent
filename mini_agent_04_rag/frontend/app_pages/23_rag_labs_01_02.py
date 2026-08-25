"""실제 pgvector·Redis를 사용하는 RAG Lab 01~02 통합 화면입니다."""

import streamlit as st

from clients.agent_client import (
    answer_with_rag, get_indexed_rag_source, index_rag_text, run_rag_agent,
)
from core.api_client import BackendAPIError


st.title("🧪 RAG Labs 01~02")
st.caption("검증된 검색 Tool · pgvector · Redis Cache · 안전한 문서 교체를 단계별로 확인합니다.")

lab_01, lab_02 = st.tabs(["01 · 고객지원 RAG Agent", "02 · 정책 문서 갱신"])

with lab_01:
    st.subheader("고객지원 정책 Agent")
    st.code(
        "Agent Tool 선택 → Backend 검증 → pgvector 검색 → Tool Result → 근거 답변\n"
        "동일 질문 답변 1회차 MISS → 2회차 Redis HIT",
        language="text",
    )
    question = st.text_input(
        "고객 질문",
        "호텔을 당일 취소하면 환불받을 수 있나요?",
        key="rag_lab_01_question",
    )
    provider = st.selectbox(
        "답변 Provider",
        ["mock", "ollama", "openai", "gemini"],
        key="rag_lab_01_provider",
    )
    mode = st.selectbox(
        "검색 방식",
        ["hybrid", "pgvector", "keyword"],
        key="rag_lab_01_mode",
    )
    if st.button("Lab 01 실행", type="primary", use_container_width=True):
        try:
            agent_result = run_rag_agent(question, provider, mode)
            first = answer_with_rag(question, mode, 3, provider, use_cache=True)
            second = answer_with_rag(question, mode, 3, provider, use_cache=True)

            st.success(agent_result["final_answer"])
            left, right = st.columns(2)
            with left:
                st.markdown("#### Agent와 Tool")
                st.json({
                    "decision": agent_result["decision"],
                    "tool_call": agent_result["tool_call"],
                    "execution": agent_result["execution"],
                    "termination_reason": agent_result["termination_reason"],
                })
            with right:
                st.markdown("#### Redis Cache")
                st.json({
                    "first": {
                        "cache_hit": first["cache_hit"],
                        "ttl": first["cache_ttl_seconds"],
                    },
                    "second": {
                        "cache_hit": second["cache_hit"],
                        "ttl": second["cache_ttl_seconds"],
                    },
                })
            with st.expander("Agent Trace", expanded=True):
                st.json(agent_result["trace"])
            with st.expander("첫 답변 Trace"):
                st.json(first["trace"])
            with st.expander("두 번째 답변 Trace"):
                st.json(second["trace"])
        except BackendAPIError as error:
            st.error(str(error))

with lab_02:
    st.subheader("정책 문서 갱신과 Cache 무효화")
    st.info(
        "같은 Source를 version 1에서 version 2로 교체합니다. 모든 Embedding과 DB "
        "Transaction이 성공한 후에만 Redis RAG Cache가 무효화됩니다."
    )
    source = st.text_input("고정 Source", "lab-hotel-refund.md", key="rag_lab_02_source")
    question_02 = st.text_input(
        "검증 질문",
        "호텔을 당일 취소하면 환불받을 수 있나요?",
        key="rag_lab_02_question",
    )
    version_1 = st.text_area(
        "version 1",
        "체크인 3일 전까지 취소하면 전액 환불합니다. 체크인 당일에는 숙박 요금의 50%를 환불합니다.",
        key="rag_lab_02_v1",
    )
    version_2 = st.text_area(
        "version 2",
        "체크인 당일 취소에는 숙박 요금 전액이 부과되며 환불되지 않습니다.",
        key="rag_lab_02_v2",
    )
    policy_filter = {"dataset": "policy_update", "source_id": source}

    if "rag_lab_02_events" not in st.session_state:
        st.session_state.rag_lab_02_events = []

    first, second, third = st.columns(3)
    if first.button("1. version 1 색인", use_container_width=True):
        try:
            indexed = index_rag_text(
                "호텔 환불 정책 v1", version_1, source,
                {
                    "dataset": "policy_update", "source_id": source,
                    "category": "hotel", "status": "active", "document_version": 1,
                },
            )
            stored = get_indexed_rag_source(source)
            st.session_state.rag_lab_02_events.append({
                "stage": "index_v1", "data": {"index": indexed, "stored": stored},
            })
            st.success("version 1 색인 완료")
        except BackendAPIError as error:
            st.error(str(error))

    if second.button("2. MISS → HIT 확인", use_container_width=True):
        try:
            miss = answer_with_rag(
                question_02, "pgvector", 3, "mock", use_cache=True,
                metadata_filter=policy_filter,
            )
            hit = answer_with_rag(
                question_02, "pgvector", 3, "mock", use_cache=True,
                metadata_filter=policy_filter,
            )
            st.session_state.rag_lab_02_events.extend([
                {"stage": "version_1_first_answer", "data": miss},
                {"stage": "version_1_second_answer", "data": hit},
            ])
            st.success(f"1회차 hit={miss['cache_hit']} · 2회차 hit={hit['cache_hit']}")
        except BackendAPIError as error:
            st.error(str(error))

    if third.button("3. version 2 교체 후 검색", type="primary", use_container_width=True):
        try:
            indexed = index_rag_text(
                "호텔 환불 정책 v2", version_2, source,
                {
                    "dataset": "policy_update", "source_id": source,
                    "category": "hotel", "status": "active", "document_version": 2,
                },
            )
            stored = get_indexed_rag_source(source)
            refreshed = answer_with_rag(
                question_02, "pgvector", 3, "mock", use_cache=True,
                metadata_filter=policy_filter,
            )
            st.session_state.rag_lab_02_events.extend([
                {"stage": "index_v2", "data": {"index": indexed, "stored": stored}},
                {"stage": "version_2_first_answer", "data": refreshed},
            ])
            st.success(f"version 2 검색 완료 · cache_hit={refreshed['cache_hit']}")
        except BackendAPIError as error:
            st.error(str(error))

    reset_column, _ = st.columns([1, 3])
    if reset_column.button("화면 Trace 초기화", use_container_width=True):
        st.session_state.rag_lab_02_events = []
    with st.expander("Lab 02 전체 Trace", expanded=True):
        st.json(st.session_state.rag_lab_02_events)
