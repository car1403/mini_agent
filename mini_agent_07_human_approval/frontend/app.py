"""mini_frontend와 같은 초보자용 Streamlit 멀티페이지 앱입니다."""

import streamlit as st

from core.state import init_state
from core.ui import render_backend_selector


st.set_page_config(page_title="Mini Agent 07", page_icon="🛡️", layout="wide")
init_state()

home_page = st.Page("app_pages/01_home.py", title="HOME", default=True)
environment_page = st.Page("app_pages/02_environment.py", title="환경 상태")
llm_page = st.Page("app_pages/03_llm.py", title="LLM과 구조화")
tool_page = st.Page("app_pages/04_tool.py", title="Tool")
knowledge_page = st.Page("app_pages/05_knowledge_memory.py", title="RAG와 Memory")
agent_page = st.Page("app_pages/06_agent.py", title="Agent 실행")
risk_page = st.Page("app_pages/07_risk.py", title="작업 위험도")
allowlist_page = st.Page("app_pages/08_allowlist.py", title="Allowlist와 소유권")
pause_page = st.Page("app_pages/09_pause_resume.py", title="중단·저장·재개")
interrupt_page = st.Page("app_pages/10_interrupt.py", title="LangGraph interrupt")
safe_page = st.Page("app_pages/11_safe_execution.py", title="안전한 실행")

pages = [
    home_page,
    environment_page,
    llm_page,
    tool_page,
    knowledge_page,
    risk_page,
    allowlist_page,
    pause_page,
    interrupt_page,
    agent_page,
    safe_page,
]

navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    st.title("🛡️ Mini Agent 07")
    st.caption("05 과정 · 07_human-approval-and-safety")
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
    with st.expander("07. Human Approval과 Safety", expanded=True):
        st.page_link(risk_page, label="7-1. 작업 위험도")
        st.page_link(allowlist_page, label="7-2. Allowlist와 소유권")
        st.page_link(pause_page, label="7-3. 중단·저장·재개")
        st.page_link(interrupt_page, label="7-4. LangGraph interrupt")
        st.page_link(agent_page, label="7-5. 승인과 거절")
        st.page_link(safe_page, label="7-6. 안전한 실행")

    st.divider()
    st.caption("실행 환경")
    render_backend_selector()
    st.page_link(environment_page, label="🩺 환경 상태")

navigation.run()
