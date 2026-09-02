import streamlit as st

from clients.learning_client import run_checkpoint
from core.api_client import ApiClientError


st.title("6-7. Checkpoint와 thread_id")
st.caption("같은 thread_id는 이전 State를 이어가고 다른 ID는 별도 실행입니다.")

thread_id = st.selectbox("thread_id", ["travel-a", "travel-b"])
if st.button("이 Thread 실행", type="primary"):
    try:
        result = run_checkpoint(thread_id)
        st.metric("visits", result["state"]["visits"])
        st.metric("Checkpoint 수", result["checkpoint_count"])
        st.json(result)
    except ApiClientError as error:
        st.error(str(error))

st.warning("InMemorySaver이므로 LangGraph Backend를 재시작하면 Checkpoint가 사라집니다.")
