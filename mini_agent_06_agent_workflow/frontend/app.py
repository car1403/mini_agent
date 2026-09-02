import streamlit as st

from core.state import init_state
from core.ui import render_backend_selector


st.set_page_config(page_title="Mini Agent 06", page_icon="🕸️", layout="wide")
init_state()

home_page = st.Page("app_pages/01_home.py", title="HOME", default=True)
environment_page = st.Page("app_pages/02_environment.py", title="환경 상태")
llm_page = st.Page("app_pages/03_llm.py", title="LLM과 구조화")
tool_page = st.Page("app_pages/04_tool.py", title="Tool")
knowledge_page = st.Page("app_pages/05_knowledge_memory.py", title="RAG와 Memory")
agent_page = st.Page("app_pages/06_agent.py", title="완성 Agent")
python_workflow_page = st.Page("app_pages/12_python_workflow.py", title="일반 Python Workflow")
graph_basics_page = st.Page("app_pages/07_graph_basics.py", title="State·Node·Edge")
branch_page = st.Page("app_pages/08_graph_branch.py", title="조건 분기")
first_graph_page = st.Page("app_pages/13_first_graph.py", title="첫 번째 Graph")
reducer_page = st.Page("app_pages/14_reducer.py", title="Reducer")
loop_page = st.Page("app_pages/09_graph_loop.py", title="반복과 종료")
checkpoint_page = st.Page("app_pages/10_graph_checkpoint.py", title="Checkpoint")
compare_page = st.Page("app_pages/11_graph_compare.py", title="Python과 비교")

pages = [
    home_page,
    python_workflow_page,
    graph_basics_page,
    branch_page,
    first_graph_page,
    reducer_page,
    loop_page,
    checkpoint_page,
    compare_page,
    environment_page,
    llm_page,
    tool_page,
    knowledge_page,
    agent_page,
]
navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    st.title("🕸️ Mini Agent 06")
    st.caption("05 과정 · 06_langgraph-workflow")
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
    with st.expander("06. LangGraph Workflow", expanded=True):
        st.page_link(python_workflow_page, label="6-1. 일반 Python Workflow")
        st.page_link(graph_basics_page, label="6-2. State·Node·Edge")
        st.page_link(branch_page, label="6-3. 조건 분기")
        st.page_link(first_graph_page, label="6-4. 첫 번째 Graph")
        st.page_link(reducer_page, label="6-5. Reducer")
        st.page_link(loop_page, label="6-6. 반복과 안전한 종료")
        st.page_link(checkpoint_page, label="6-7. Checkpoint와 thread_id")
        st.page_link(compare_page, label="6-8. Python과 LangGraph 비교")

    st.divider()
    st.caption("선택 · 완성본 확인")
    render_backend_selector()
    st.page_link(environment_page, label="🩺 환경 상태")
    st.page_link(llm_page, label="🤖 LLM과 구조화")
    st.page_link(tool_page, label="🧰 Tool")
    st.page_link(knowledge_page, label="📚 RAG와 Memory")
    st.page_link(agent_page, label="🧭 완성 Agent")

navigation.run()
