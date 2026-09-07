import streamlit as st
from frontend.core.ui import media_inputs, start_run, show_run

st.title("안내문 촬영 시설 도우미 Agent")
st.write("안내문을 촬영하면 MCP Tool로 이용 규정을 검색하고, 현재 일정과 잔여 정원을 조회합니다.")
st.info("예시: PG-YOGA는 초보자도 참여할 수 있나요? 앞으로 4주간 토요일 자리를 확인해 주세요.")
try:
    image, question, audio, speak = media_inputs("facility")
    if st.button("시설 Agent 실행",type="primary"):
        start_run("facility",image,question,audio,speak)
    show_run("facility")
except Exception as exc:
    st.error(f"요청을 처리하지 못했습니다: {exc}")
