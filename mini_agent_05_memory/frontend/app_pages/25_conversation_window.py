import streamlit as st

from clients.agent_client import preview_conversation_window
from core.api_client import BackendAPIError


st.title("5-2. 대화 Window")
st.caption("전체 대화 대신 최근 메시지와 오래된 대화의 요약만 사용합니다.")

messages = [
    {"role": "user", "content": "부산으로 여행 갈 거예요."},
    {"role": "assistant", "content": "며칠 일정인가요?"},
    {"role": "user", "content": "2박 3일이에요."},
    {"role": "assistant", "content": "교통수단 선호가 있나요?"},
    {"role": "user", "content": "대중교통을 이용하고 싶어요."},
    {"role": "assistant", "content": "숙소 선호도 알려주세요."},
]
max_recent = st.slider("최근에 유지할 메시지 수", 1, len(messages), 3)

if st.button("대화 Window 만들기", type="primary"):
    try:
        result = preview_conversation_window(messages, max_recent)
        st.metric("전체 메시지", result["total_count"])
        st.subheader("오래된 대화 요약")
        st.write(result["older_summary"])
        st.subheader("최근 메시지")
        st.json(result["recent_messages"])
    except BackendAPIError as error:
        st.error(str(error))
