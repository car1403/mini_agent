import streamlit as st

from core.ui import backend_request, run_api
from core.state import selected_provider


st.title("🤖 LLM과 Structured Output")
provider_label, provider = selected_provider()
st.caption(f"현재 Provider: {provider_label}")
message = st.text_area(
    "여행 요청",
    "부산에서 대중교통으로 즐기는 2박 3일 여행을 제안해 주세요.",
)

plain, structured = st.columns(2)
if plain.button("일반 응답"):
    data = run_api(
        lambda: backend_request(
            "POST",
            "/api/providers/generate",
            {"provider": provider, "message": message},
        )
    )
    if data:
        st.write(data["content"])
        st.caption(f"{data['provider']} / {data['model']} / {data['latency_ms']}ms")

if structured.button("TravelPlan 구조화 응답"):
    data = run_api(
        lambda: backend_request(
            "POST",
            "/api/providers/travel-plan",
            {"provider": provider, "message": message},
        )
    )
    if data:
        st.json(data["content"])
        st.caption(f"{data['provider']} / {data['model']} / {data['latency_ms']}ms")

st.divider()
st.subheader("자연어 요청 구조화")
extract_message = st.text_area(
    "분석할 요청",
    "8월 부산 2박 여행을 성인 2명이 가고 싶어요. 예산은 50만 원이고 대중교통을 이용할게요.",
    key="extract_message",
)
if st.button("요청 추출"):
    data = run_api(
        lambda: backend_request(
            "POST", "/api/travel/extract", {"message": extract_message}
        )
    )
    if data:
        st.dataframe([data], use_container_width=True)
        st.json(data)
