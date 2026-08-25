"""검색 평가와 Redis 상태 기반 Multi-Tool RAG Agent 화면입니다."""

import uuid

import streamlit as st

from clients.agent_client import (
    reset_multi_tool_rag_agent, run_multi_tool_rag_agent,
    run_rag_retrieval_evaluation, seed_multi_tool_rag_documents,
    seed_rag_evaluation_documents,
)
from core.api_client import BackendAPIError


st.title("🧪 RAG Labs 06~07")
st.caption("검색 순위를 정량 평가하고 Redis에 상태를 유지하는 Multi-Tool Agent를 실행합니다.")

evaluation_tab, agent_tab = st.tabs(["06 · 검색 품질 평가", "07 · Multi-Tool RAG Agent"])

with evaluation_tab:
    st.subheader("Keyword·Vector·Hybrid Hit@K와 MRR")
    if st.button("평가 Dataset pgvector 색인", use_container_width=True):
        try:
            result = seed_rag_evaluation_documents()
            st.success("4개 정답 문서를 색인했습니다.")
            st.json(result)
        except BackendAPIError as error:
            st.error(str(error))
    top_k = st.slider("평가 top_k", 1, 4, 3)
    if st.button("검색 품질 평가", type="primary", use_container_width=True):
        try:
            result = run_rag_retrieval_evaluation(top_k)
            columns = st.columns(3)
            for column, report in zip(columns, result["reports"]):
                with column:
                    st.markdown(f"#### {report['mode']}")
                    st.metric(f"Hit@{top_k}", f"{report['hit_at_k']:.3f}")
                    st.metric("MRR", f"{report['mrr']:.3f}")
                    st.json(report["cases"])
        except BackendAPIError as error:
            st.error(str(error))

with agent_tab:
    st.subheader("재질문·여러 지식 저장소·종료 조건")
    if "multi_rag_session_id" not in st.session_state:
        st.session_state.multi_rag_session_id = str(uuid.uuid4())
    if "multi_rag_history" not in st.session_state:
        st.session_state.multi_rag_history = []

    if st.button("호텔·항공·관광 문서 pgvector 색인", use_container_width=True):
        try:
            result = seed_multi_tool_rag_documents()
            st.success("세 지식 영역의 문서를 색인했습니다.")
            st.json(result)
        except BackendAPIError as error:
            st.error(str(error))

    provider = st.selectbox(
        "최종 답변 Provider", ["mock", "ollama", "openai", "gemini"],
        key="multi_rag_provider",
    )
    message = st.text_input(
        "사용자 메시지",
        "여행 규정을 알려 주세요." if not st.session_state.multi_rag_history
        else "호텔 당일 취소와 항공 수하물 규정이 궁금합니다.",
        key=f"multi_rag_message_{len(st.session_state.multi_rag_history)}",
    )
    run_column, reset_column = st.columns(2)
    if run_column.button("Agent Cycle 실행", type="primary", use_container_width=True):
        try:
            result = run_multi_tool_rag_agent(
                st.session_state.multi_rag_session_id, message, provider,
            )
            st.session_state.multi_rag_history.append(result)
            if result["status"] == "completed":
                st.success(result["final_answer"])
            elif result["status"] == "needs_clarification":
                st.info(result["final_answer"])
            else:
                st.warning(result["final_answer"])
        except BackendAPIError as error:
            st.error(str(error))
    if reset_column.button("Redis Agent 상태 초기화", use_container_width=True):
        try:
            reset_multi_tool_rag_agent(st.session_state.multi_rag_session_id)
            st.session_state.multi_rag_history = []
            st.session_state.multi_rag_session_id = str(uuid.uuid4())
            st.success("새 Agent Session을 시작합니다.")
        except BackendAPIError as error:
            st.error(str(error))

    if st.session_state.multi_rag_history:
        latest = st.session_state.multi_rag_history[-1]
        left, right = st.columns(2)
        with left:
            st.markdown("#### Agent 상태")
            st.json({
                "topics": latest["topics"],
                "step_count": latest["step_count"],
                "max_steps": latest["max_steps"],
                "termination_reason": latest["termination_reason"],
            })
        with right:
            st.markdown("#### Tool Calls")
            st.json(latest["tool_calls"])
        with st.expander("Tool Results", expanded=True):
            st.json(latest["tool_results"])
        with st.expander("전체 Redis 상태 Trace", expanded=True):
            st.json(latest["trace"])
