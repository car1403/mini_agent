import streamlit as st

from clients.agent_client import complete_tool_loop
from core.api_client import BackendAPIError


st.title("🔁 Tool Result로 최종 답변 만들기")
st.caption("LLM 선택 → Python Tool 실행 → LLM 최종 답변의 세 단계를 확인합니다.")

tool_choice = st.selectbox("Tool Choice", ["auto", "none", "required"])
message = st.selectbox(
    "질문",
    [
        "오늘 부산 날씨를 알려줘",
        "제주 숙소를 찾아줘",
        "서울 관광지를 추천해줘",
        "여행을 준비하고 있어요",
    ],
)

st.code("질문 → ① LLM이 Tool 선택 → ② Python이 실행 → ③ LLM이 최종 답변", language="text")

if st.button("Agent Cycle 실행", type="primary"):
    try:
        result = complete_tool_loop(message, tool_choice)
        st.subheader("1. LLM이 Tool과 arguments 선택")
        st.json(result["decision"])
        st.subheader("2. Python Backend가 Tool 실행")
        if result["decision"]["needs_clarification"]:
            st.warning(result["decision"]["follow_up_question"])
        elif result["tool_result"] is None:
            st.info("실행할 Tool이 없습니다.")
        else:
            st.json(result["tool_result"])
        st.subheader("3. LLM이 사용자용 최종 답변 생성")
        st.success(result["final_answer"])
        with st.expander("전체 Cycle Trace", expanded=True):
            st.json(result["trace"])
    except BackendAPIError as error:
        st.error(str(error))
