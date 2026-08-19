import streamlit as st

from clients.agent_client import compare_structured_outputs
from core.api_client import BackendAPIError


st.title("🧱 Structured Output")
st.caption("생성형 TravelPlan과 분류형 SupportTicket 계약을 Provider별로 비교합니다.")
schema_options = {
    "여행 계획 (TravelPlan)": ("travel_plan", "부산에서 대중교통으로 즐기는 2박 3일 여행을 제안해 주세요."),
    "고객 문의 (SupportTicket)": ("support_ticket", "결제가 두 번 된 것 같습니다. 주문 번호는 아직 찾지 못했습니다."),
}
selected_schema = st.selectbox("Structured Output Schema", list(schema_options))
schema_type, default_message = schema_options[selected_schema]
providers = st.multiselect(
    "비교할 Provider", ["mock", "gemini", "openai", "ollama"], default=["mock"]
)
message = st.text_area("사용자 요청", default_message, key=f"message-{schema_type}")
cloud_calls = len([item for item in providers if item in {"gemini", "openai"}])
st.info(f"총 {len(providers)}회 호출, Cloud API {cloud_calls}회입니다. 먼저 Mock으로 계약을 확인하세요.")

if st.button("구조화 결과 비교", disabled=not providers):
    try:
        result = compare_structured_outputs(providers, message, schema_type)
        for item in result["results"]:
            with st.container(border=True):
                st.subheader(item["provider"])
                if item["status"] == "success":
                    st.caption(f"{item['model']} · {item['latency_ms']} ms · {selected_schema} 검증 성공")
                    st.json(item["content"])
                else:
                    st.error(item["error"])
    except BackendAPIError as error:
        st.error(str(error))
