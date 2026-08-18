import streamlit as st

from clients.agent_client import classify_travel
from core.api_client import BackendAPIError


st.title("🧳 여행 요청 분류")
message = st.text_input("요청", "부산 2박 3일 여행 코스를 만들어 줘.")
if st.button("요청 분류"):
    try:
        result = classify_travel(message)
        st.json(result)
        if result["follow_up_question"]:
            st.warning(result["follow_up_question"])
    except BackendAPIError as error:
        st.error(str(error))
