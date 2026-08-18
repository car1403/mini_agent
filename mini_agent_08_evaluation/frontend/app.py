"""mini_frontend와 같은 초보자용 Streamlit 멀티페이지 앱입니다."""

import streamlit as st

from core.state import init_state
from core.ui import render_backend_selector


st.set_page_config(page_title="Mini Agent 08", page_icon="📊", layout="wide")
init_state()

home_page = st.Page("app_pages/01_home.py", title="HOME", default=True)
environment_page = st.Page("app_pages/02_environment.py", title="환경 상태")
llm_page = st.Page("app_pages/03_llm.py", title="LLM과 구조화")
tool_page = st.Page("app_pages/04_tool.py", title="Tool")
knowledge_page = st.Page("app_pages/05_knowledge_memory.py", title="RAG와 Memory")
agent_page = st.Page("app_pages/06_agent.py", title="Agent 실행")
why_page = st.Page("app_pages/07_why_evaluate.py", title="평가가 필요한 이유")
one_page = st.Page("app_pages/08_one_scenario.py", title="시나리오 하나")
multiple_page = st.Page("app_pages/09_multiple_scenarios.py", title="여러 시나리오")
trace_page = st.Page("app_pages/10_trace_failure.py", title="Trace 실패 찾기")
regression_page = st.Page("app_pages/11_regression.py", title="회귀 테스트")
provider_page = st.Page("app_pages/12_provider_comparison.py", title="Provider 비교 (선택)")

pages = [
    home_page,
    environment_page,
    llm_page,
    tool_page,
    knowledge_page,
    agent_page,
    why_page,
    one_page,
    multiple_page,
    trace_page,
    regression_page,
    provider_page,
]

navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    st.title("📊 Mini Agent 08")
    st.caption("05 과정 · 08_agent-evaluation-and-tracing")
    st.page_link(home_page, label="🏠 HOME")

    st.divider()
    with st.expander("01. LLM에서 Agent로", expanded=False):
        st.page_link(llm_page, label="1단계 핵심 복습")

    st.divider()
    with st.expander("02. Prompt와 구조화 출력", expanded=False):
        st.page_link(llm_page, label="2단계 핵심 복습")

    st.divider()
    with st.expander("03. Tool Use", expanded=False):
        st.page_link(tool_page, label="3단계 핵심 복습")

    st.divider()
    with st.expander("04. RAG", expanded=False):
        st.page_link(knowledge_page, label="4단계 핵심 복습")

    st.divider()
    with st.expander("05. Memory", expanded=False):
        st.page_link(knowledge_page, label="5단계 핵심 복습")

    st.divider()
    with st.expander("06. LangGraph Workflow", expanded=False):
        st.caption("Mini Agent 06에서 Graph 흐름을 복습합니다.")

    st.divider()
    with st.expander("07. Human Approval과 Safety", expanded=False):
        st.page_link(agent_page, label="7단계 승인 흐름 복습")

    st.divider()
    with st.expander("08. Evaluation과 Tracing", expanded=True):
        st.page_link(why_page, label="8-1. 평가가 필요한 이유")
        st.page_link(one_page, label="8-2. 시나리오 하나")
        st.page_link(multiple_page, label="8-3. 여러 시나리오")
        st.page_link(trace_page, label="8-4. Trace 실패 찾기")
        st.page_link(regression_page, label="8-5. 회귀 테스트")
        st.page_link(provider_page, label="8-6. Provider 비교 (선택)")

    st.divider()
    st.caption("실행 환경과 완성본")
    render_backend_selector()
    st.page_link(environment_page, label="🩺 환경 상태")
    st.page_link(agent_page, label="🧭 완성 Agent")

navigation.run()
