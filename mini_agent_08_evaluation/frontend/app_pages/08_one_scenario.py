import streamlit as st

from core.ui import backend_request, run_api, show_json


st.title("8-2. 시나리오 하나")
st.caption("입력과 기대 행동을 적고 실제 Agent 결과와 비교합니다.")

name = st.text_input("시나리오 이름", "날씨 조회")
message = st.text_input("입력", "부산 날씨를 알려줘")
expected_tool_label = st.selectbox(
    "기대 Tool", ["get_weather", "search_hotels", "search_attractions", "없음"]
)
expected_status = st.selectbox("기대 상태", ["completed", "needs_input", "blocked"])

if st.button("시나리오 평가", type="primary"):
    report = run_api(
        lambda: backend_request(
            "POST",
            "/api/evaluations/run",
            {
                "scenarios": [
                    {
                        "name": name,
                        "message": message,
                        "expected_tool": None if expected_tool_label == "없음" else expected_tool_label,
                        "expected_status": expected_status,
                    }
                ]
            },
        )
    )
    if report:
        result = report["results"][0]
        st.success("통과했습니다.") if result["passed"] else st.error("실패했습니다.")
        st.json({"expected": result["expected"], "actual": result["actual"], "checks": result["checks"]})
        show_json(result)
