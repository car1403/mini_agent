import streamlit as st

from clients.agent_client import complete_tool_loop
from core.api_client import BackendAPIError


st.title("🔁 Tool Result로 최종 답변 만들기")
st.caption("Agent의 선택·검증·실행·최종 답변 단계를 한 번에 추적합니다.")

provider = st.selectbox("Provider", ["mock", "gemini", "openai", "ollama"])
message = st.selectbox(
    "질문",
    [
        "부산 날씨를 알려줘",
        "제주 숙소를 찾아줘",
        "서울 관광지를 추천해줘",
        "여행을 준비하고 있어요",
    ],
)

st.code("질문 → Tool Call → Backend 검증 → Tool Result → 최종 답변", language="text")

if st.button("Agent Loop 실행", type="primary"):
    try:
        result = complete_tool_loop(provider, message)
        st.subheader("1. Tool Call 제안")
        st.json(result["decision"])
        st.subheader("2. Backend Tool Result")
        if result["tool_result"] is None:
            st.info("실행할 Tool이 없습니다.")
        else:
            st.json(result["tool_result"])
        st.subheader("3. 사용자용 최종 답변")
        st.success(result["final_answer"])
    except BackendAPIError as error:
        st.error(str(error))
