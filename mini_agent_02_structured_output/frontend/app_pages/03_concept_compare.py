import streamlit as st

from clients.agent_client import compare_concepts
from core.api_client import BackendAPIError


st.title("🧭 LLM·Workflow·Agent")
st.caption("같은 요청을 고정 Workflow와 의미 기반 Mock Router로 비교합니다.")
message = st.text_input("요청", "내일 비가 올까요?")

if st.button("판단 비교"):
    try:
        result = compare_concepts(message)
        left, right = st.columns(2)
        with left:
            st.subheader("고정 Workflow")
            st.json(result["workflow"])
        with right:
            st.subheader("의미 기반 Mock Router")
            st.json(result["semantic_router"])
        st.info(result["note"])
    except BackendAPIError as error:
        st.error(str(error))
