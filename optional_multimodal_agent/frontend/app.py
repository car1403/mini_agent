"""mini_frontend와 같은 초보자용 Streamlit 멀티페이지 진입점입니다."""

import streamlit as st

from core.state import init_state
from core.ui import render_backend_selector


st.set_page_config(
    page_title="Optional Multimodal Agent",
    page_icon="🧭",
    layout="wide",
)
init_state()

home_page = st.Page("app_pages/01_home.py", title="HOME", default=True)
environment_page = st.Page("app_pages/02_environment.py", title="환경 상태")
llm_page = st.Page("app_pages/03_llm.py", title="LLM과 구조화")
tool_page = st.Page("app_pages/04_tool.py", title="Tool")
knowledge_page = st.Page("app_pages/05_knowledge_memory.py", title="RAG와 Memory")
agent_page = st.Page("app_pages/06_agent.py", title="Agent 실행")
evaluation_page = st.Page("app_pages/07_evaluation.py", title="Provider 평가")
multimodal_page = st.Page("app_pages/08_multimodal.py", title="이미지와 음성")

pages = [
    home_page,
    environment_page,
    llm_page,
    tool_page,
    knowledge_page,
    agent_page,
    evaluation_page,
    multimodal_page,
]

navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    st.title("🖼️ Optional Multimodal Agent")
    render_backend_selector()
    st.divider()
    st.page_link(home_page, label="🏠 HOME")
    st.page_link(environment_page, label="🧰 환경 상태")
    st.page_link(llm_page, label="🧠 LLM과 구조화")
    st.page_link(tool_page, label="🛠️ Tool")
    st.page_link(knowledge_page, label="📚 RAG와 Memory")
    st.page_link(agent_page, label="🧭 Agent 실행")
    st.page_link(evaluation_page, label="📊 Provider 평가")
    st.page_link(multimodal_page, label="🖼️ 이미지와 음성")

navigation.run()
