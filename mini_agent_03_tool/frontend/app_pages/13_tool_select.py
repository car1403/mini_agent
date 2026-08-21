import streamlit as st

from clients.agent_client import get_tools, select_tool
from core.api_client import BackendAPIError


st.title("🧭 Tool 선택")
st.caption("LLM은 Tool Call을 제안할 뿐, 이 화면에서는 아직 함수를 실행하지 않습니다.")

try:
    registry = get_tools()
    with st.expander("허용된 조회 Tool과 입력 Schema"):
        st.json(registry)
except BackendAPIError as error:
    st.error(str(error))

st.caption("OpenAI가 질문과 Tool 설명을 보고 사용할 Tool을 선택합니다.")
tool_choice = st.selectbox("Tool Choice", ["auto", "none", "required"])
message = st.selectbox("요청", ["지금 부산에 비가 와?", "내일 부산에 비가 올까?", "부산 숙소를 찾아줘.", "제주 관광지를 추천해 줘.", "여행 준비를 도와줘."])

if st.button("Tool Call 제안 받기"):
    try:
        decision = select_tool(message, tool_choice)
        st.session_state["tool_decision"] = decision
        st.json(decision)
        if decision["needs_clarification"]:
            st.warning(decision["follow_up_question"])
        with st.expander("LLM이 반환한 Tool Call 원본"):
            st.json(decision["raw_tool_call"])
        st.info("아직 Tool 함수는 실행되지 않았습니다. 다음 메뉴에서 arguments를 확인하고 실행합니다.")
    except BackendAPIError as error:
        st.error(str(error))
