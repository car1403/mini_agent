import streamlit as st

from clients.agent_client import compare_providers
from core.api_client import BackendAPIError


st.title("⚖️ Provider 비교")
st.caption("동일한 Prompt에 대한 Gemini, GPT, Ollama/Llama의 결과를 비교합니다.")
providers = st.multiselect("비교할 Provider", ["mock", "gemini", "openai", "ollama"], default=["mock"])
system_prompt = st.text_area("System Prompt", "당신은 초보자를 돕는 친절한 여행 도우미입니다.")
message = st.text_area("같은 질문", "부산 2박 여행을 준비할 때 먼저 확인할 것은 무엇인가요?")
cloud_calls = len([item for item in providers if item in {"gemini", "openai"}])
st.info(f"총 {len(providers)}회 호출하며 Cloud API 호출은 {cloud_calls}회입니다.")

if st.button("선택한 Provider 비교", disabled=not providers):
    try:
        with st.spinner("Provider 응답을 비교하는 중입니다..."):
            result = compare_providers(providers, system_prompt, message)
        for item in result["results"]:
            with st.container(border=True):
                st.subheader(item["provider"])
                if item["status"] == "success":
                    st.caption(f"{item['model']} · {item['latency_ms']} ms")
                    st.write(item["content"])
                else:
                    st.error(item["error"])
    except BackendAPIError as error:
        st.error(str(error))
