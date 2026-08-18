import streamlit as st

from core.ui import backend_request, run_api


st.title("8-6. Provider 비교 (선택)")
st.caption("같은 구조화 요청을 설정된 Provider에 한 번씩 실행해 관찰합니다.")
st.warning("Mock 이외 Provider는 API 설정, 로컬 Ollama 실행, 비용 또는 대기 시간이 필요할 수 있습니다.")

provider = st.selectbox("Provider", ["mock", "openai", "gemini", "ollama"])
message = st.text_area("동일한 요청", "부산의 대표 장소를 포함한 2박 3일 여행을 제안해 주세요.")

if st.button("선택한 Provider 실행", type="primary"):
    data = run_api(
        lambda: backend_request(
            "POST",
            "/api/providers/travel-plan",
            {"provider": provider, "message": message},
        )
    )
    if data:
        st.session_state.provider_results.append(
            {
                "provider": data["provider"],
                "model": data["model"],
                "latency_ms": data["latency_ms"],
                "structured": isinstance(data["content"], dict),
                "fallback_used": data.get("fallback_used", False),
            }
        )
        st.json(data["content"])

if st.session_state.provider_results:
    st.subheader("이번 세션의 비교 결과")
    st.dataframe(st.session_state.provider_results, use_container_width=True)
    if st.button("비교 결과 비우기"):
        st.session_state.provider_results = []
        st.rerun()

st.info("응답 한 번으로 Provider의 우열을 단정하지 않습니다. 같은 시나리오를 여러 번 평가해야 합니다.")
