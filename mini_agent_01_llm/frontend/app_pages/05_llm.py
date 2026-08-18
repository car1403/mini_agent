import streamlit as st

from clients.agent_client import generate_response
from core.api_client import BackendAPIError


st.title("🤖 LLM 호출")
st.caption("Mock으로 연결을 확인한 뒤 Gemini, GPT, Ollama/Llama 순서로 비교합니다.")
provider = st.selectbox("Provider", ["mock", "gemini", "openai", "ollama"])
system_prompt = st.text_area("System Prompt", "당신은 초보자를 돕는 친절한 여행 도우미입니다.")
message = st.text_area("질문", "부산에서 대중교통으로 즐길 수 있는 2박 3일 여행을 추천해 주세요.")

if st.button("LLM 호출"):
    try:
        with st.spinner("LLM 응답을 기다리는 중입니다..."):
            result = generate_response(provider, system_prompt, message)
        st.subheader("응답")
        st.write(result["content"])
        col1, col2, col3 = st.columns(3)
        col1.metric("Provider", result["provider"])
        col2.metric("Model", result["model"])
        col3.metric("응답 시간", f"{result['latency_ms']} ms")
    except BackendAPIError as error:
        st.error(str(error))
