import streamlit as st


st.title("7-4. LangGraph interrupt")
st.caption("Graph를 중단하고 외부의 승인 값을 기다립니다.")

st.code(
    "decision = interrupt({\n"
    "    'question': 'Mock 예약을 승인하시겠습니까?',\n"
    "    'allowed_actions': ['approve', 'reject'],\n"
    "})\n\n"
    "graph.invoke(Command(resume={\n"
    "    'decision': 'approve',\n"
    "    'actor': 'demo-user',\n"
    "}), config=config)",
    language="python",
)
st.warning("재개할 때도 중단할 때 사용한 것과 같은 thread_id가 필요합니다.")
