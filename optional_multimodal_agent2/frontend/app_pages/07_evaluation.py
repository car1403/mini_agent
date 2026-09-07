import streamlit as st

from core.config import PROVIDERS
from core.ui import backend_request, run_api


st.title("📊 멀티 LLM 평가")
st.warning("실제 API 호출 비용과 시간이 발생할 수 있습니다.")

labels = st.multiselect(
    "평가할 Provider",
    ["GPT", "Gemini", "Ollama/Llama"],
    default=["GPT"],
    max_selections=3,
)
providers = [PROVIDERS[label] for label in labels]
st.caption(f"예상 호출 수: {len(providers) * 3}회")

if st.button("Tool 선택 평가 실행", disabled=not providers):
    report = run_api(
        lambda: backend_request(
            "POST",
            "/api/evaluations/run",
            {"providers": providers, "scenario_set": "tool_selection"},
        )
    )
    if report:
        summary = [
            {
                "provider": item["provider"],
                "status": item["status"],
                "accuracy": item.get("accuracy"),
                "average_latency_ms": item.get("average_latency_ms"),
                "error": item.get("error"),
            }
            for item in report["results"]
        ]
        st.dataframe(summary, use_container_width=True)
        with st.expander("시나리오별 결과"):
            st.json(report)
