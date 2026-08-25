import streamlit as st

from clients.agent_client import compare_structured_outputs
from core.api_client import BackendAPIError


st.title("🧱 Structured Output")
providers = st.multiselect("Provider", ["mock", "gemini", "openai", "ollama"], default=["mock"], key="structured_providers")
message = st.text_area("여행 요청", "부산 2박 3일 여행을 제안해 주세요.", key="structured_message")
if st.button("TravelPlan 비교", disabled=not providers):
    try:
        result = compare_structured_outputs(providers, message)
        for item in result["results"]:
            with st.container(border=True):
                st.subheader(item["provider"])
                if item["status"] == "success":
                    st.json(item["content"])
                else:
                    st.error(item["error"])
    except BackendAPIError as error:
        st.error(str(error))
