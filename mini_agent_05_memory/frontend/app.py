import streamlit as st


st.set_page_config(page_title="Mini Agent 05 · Memory", page_icon="🧠", layout="wide")

memory_types = st.Page("app_pages/24_memory_types.py", title="Memory 종류", default=True)
conversation = st.Page("app_pages/25_conversation_window.py", title="대화 Window")
memory_isolation = st.Page("app_pages/26_memory_isolation.py", title="사용자 범위")
memory_crud = st.Page("app_pages/27_memory_crud.py", title="Memory CRUD")
memory_answer = st.Page("app_pages/28_memory_answer.py", title="관련 Memory와 개인화")
memory_storage = st.Page("app_pages/29_memory_storage.py", title="Redis·PostgreSQL")
memory_restore = st.Page("app_pages/30_memory_restore.py", title="Hybrid 복원")
memory_mcp = st.Page("app_pages/31_memory_mcp.py", title="PostgreSQL HTTP MCP")

pages = [
    memory_types,
    conversation,
    memory_isolation,
    memory_crud,
    memory_answer,
    memory_storage,
    memory_restore,
    memory_mcp,
]
navigation = st.navigation(pages, position="hidden")

with st.sidebar:
    st.title("🧠 Mini Agent 05")
    st.caption("Memory만 배우는 전용 화면")
    for index, page in enumerate(pages, start=1):
        st.page_link(page, label=f"5-{index}. {page.title}")
    st.divider()
    st.info("RAG는 외부 지식, Memory는 사용자와 실행 상태를 다룹니다.")

navigation.run()
