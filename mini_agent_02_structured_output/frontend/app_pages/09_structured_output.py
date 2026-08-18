import streamlit as st

from clients.agent_client import compare_structured_outputs
from core.api_client import BackendAPIError


st.title("🧱 Structured Output")
st.caption("모든 Provider가 같은 TravelPlan Schema를 반환하도록 요청하고 검증합니다.")
providers = st.multiselect(
    "비교할 Provider", ["mock", "gemini", "openai", "ollama"], default=["mock"]
)
message = st.text_area("여행 요청", "부산에서 대중교통으로 즐기는 2박 3일 여행을 제안해 주세요.")
cloud_calls = len([item for item in providers if item in {"gemini", "openai"}])
st.info(f"총 {len(providers)}회 호출, Cloud API {cloud_calls}회입니다. 먼저 Mock으로 계약을 확인하세요.")

if st.button("구조화 결과 비교", disabled=not providers):
    try:
        result = compare_structured_outputs(providers, message)
        for item in result["results"]:
            with st.container(border=True):
                st.subheader(item["provider"])
                if item["status"] == "success":
                    st.caption(f"{item['model']} · {item['latency_ms']} ms · TravelPlan 검증 성공")
                    st.json(item["content"])
                else:
                    st.error(item["error"])
    except BackendAPIError as error:
        st.error(str(error))
