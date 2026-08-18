import streamlit as st

from clients.agent_client import compare_providers
from core.api_client import BackendAPIError


st.title("⚖️ Provider 비교")
st.caption("동일한 Prompt에 대한 자유 텍스트 응답과 실패를 비교합니다.")
providers = st.multiselect("비교할 Provider", ["mock", "gemini", "openai", "ollama"], default=["mock"])
message = st.text_area("같은 질문", "부산 2박 여행을 준비할 때 먼저 확인할 것은 무엇인가요?")
cloud_calls = len([item for item in providers if item in {"gemini", "openai"}])
st.info(f"총 {len(providers)}회 호출, Cloud API {cloud_calls}회입니다.")

if st.button("일반 응답 비교", disabled=not providers):
    try:
        result = compare_providers(providers, message)
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
