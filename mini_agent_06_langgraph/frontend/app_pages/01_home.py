import streamlit as st


st.title("🏠 Mini Agent 06 · 초보자 LangGraph")
st.info("이번 단계는 복잡한 Agent를 만드는 시간이 아니라 일반 Python Workflow를 Graph로 표현하는 시간입니다.")

st.code(
    "일반 Python 함수\n"
    "  ↓\n"
    "State → Node → Edge → 조건 분기 → Reducer → 반복 → Checkpoint",
    language="text",
)

st.subheader("권장 진행")
st.write("먼저 learning_unit 01~04를 실행한 뒤 화면의 Graph 구성 요소부터 순서대로 진행하세요.")

st.warning("완성 Agent에는 승인 interrupt가 포함되어 있습니다. 승인과 재개는 다음 과정에서 설명합니다.")
