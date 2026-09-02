import streamlit as st

from clients.learning_client import compare_workflows
from core.api_client import ApiClientError


st.title("6-8. Python과 LangGraph 비교")

message = st.selectbox("입력", ["부산 여행을 준비해줘", "여행을 준비해줘"])
if st.button("같은 입력으로 비교", type="primary"):
    try:
        result = compare_workflows(message)
        left, right = st.columns(2)
        with left:
            st.subheader("일반 Python")
            st.json(result["python"])
        with right:
            st.subheader("LangGraph")
            st.json(result["langgraph"])
        st.info(result["note"])
    except ApiClientError as error:
        st.error(str(error))
