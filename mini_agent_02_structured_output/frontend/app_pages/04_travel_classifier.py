import streamlit as st

from clients.agent_client import classify_travel
from core.api_client import BackendAPIError


st.title("🧳 여행 요청 분류")
st.caption("분류 결과뿐 아니라 confidence, 누락 정보, 다음 행동을 확인합니다.")
samples = [
    "부산 2박 3일 여행 코스를 만들어 줘.",
    "호텔을 하루 전에 취소하면 수수료가 있나요?",
    "제주도에 우산을 가져가야 할까요?",
    "여행을 준비해 줘.",
    "도와주세요.",
]
selected = st.selectbox("예제 선택", samples)
custom_message = st.text_input("직접 입력 (선택)")
message = custom_message.strip() or selected

if st.button("여행 요청 분류"):
    try:
        result = classify_travel(message)
        col1, col2, col3 = st.columns(3)
        col1.metric("Intent", result["intent"])
        col2.metric("Confidence", f"{result['confidence']:.2f}")
        col3.metric("다음 행동", result["next_action"])
        st.write("판단 이유:", result["reason"])
        st.write("누락 정보:", result["missing_information"] or "없음")
        if result["follow_up_question"]:
            st.warning(result["follow_up_question"])
    except BackendAPIError as error:
        st.error(str(error))
