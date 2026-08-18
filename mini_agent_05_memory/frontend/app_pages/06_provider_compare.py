import streamlit as st

from clients.agent_client import compare_providers
from core.api_client import BackendAPIError


st.title("⚖️ Provider 비교")
providers = st.multiselect("Provider", ["mock", "gemini", "openai", "ollama"], default=["mock"])
message = st.text_area("같은 질문", "부산 여행을 준비할 때 먼저 확인할 것은 무엇인가요?")
if st.button("일반 응답 비교", disabled=not providers):
    try:
        result = compare_providers(providers, message)
        for item in result["results"]:
            with st.container(border=True):
                st.subheader(item["provider"])
                st.write(item["content"] if item["status"] == "success" else item["error"])
    except BackendAPIError as error:
        st.error(str(error))
