import streamlit as st

from clients.agent_client import generate_response
from core.api_client import BackendAPIError


st.title("🤖 LLM 호출")
st.caption("먼저 자유로운 텍스트 응답을 확인합니다. 다음 메뉴에서 구조화 결과와 비교합니다.")
provider = st.selectbox("Provider", ["mock", "gemini", "openai", "ollama"])
system_prompt = st.text_area("System Prompt", "당신은 초보자를 돕는 친절한 여행 도우미입니다.")
message = st.text_area("질문", "부산에서 대중교통으로 즐기는 2박 3일 여행을 추천해 주세요.")

if st.button("LLM 호출"):
    try:
        result = generate_response(provider, system_prompt, message)
        st.write(result["content"])
        st.caption(f"{result['provider']} · {result['model']} · {result['latency_ms']} ms")
    except BackendAPIError as error:
        st.error(str(error))
