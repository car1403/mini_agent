import streamlit as st


st.title("6-5. Reducer")
st.caption("State 값을 새 값으로 교체할지 기존 값 뒤에 누적할지 정합니다.")

st.code(
    "from operator import add\n"
    "from typing import Annotated, TypedDict\n\n"
    "class State(TypedDict):\n"
    "    trace: Annotated[list[str], add]\n\n"
    "def node(state: State) -> dict:\n"
    "    return {'trace': ['node']}\n",
    language="python",
)

left, right = st.columns(2)
left.metric("Reducer 없음", "['create_plan']")
right.metric("Reducer 있음", "['extract', 'create_plan']")
st.info("trace와 메시지 목록처럼 계속 쌓아야 하는 필드에 Reducer를 사용합니다.")
