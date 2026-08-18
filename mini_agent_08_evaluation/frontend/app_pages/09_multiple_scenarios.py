import streamlit as st

from core.ui import backend_request, run_api, show_json


st.title("8-3. 여러 시나리오")
st.caption("외부 LLM 없이 같은 기본 시나리오를 반복 평가합니다.")

if st.button("기본 5개 평가", type="primary"):
    report = run_api(lambda: backend_request("POST", "/api/evaluations/run", {}))
    if report:
        summary = report["summary"]
        col1, col2, col3 = st.columns(3)
        col1.metric("통과", summary["passed"])
        col2.metric("실패", summary["failed"])
        col3.metric("통과율", f"{summary['pass_rate'] * 100:.0f}%")
        rows = [
            {
                "시나리오": item["scenario"],
                "기대 Tool": item["expected"]["tool"],
                "실제 Tool": item["actual"]["tool"],
                "기대 상태": item["expected"]["status"],
                "실제 상태": item["actual"]["status"],
                "통과": item["passed"],
            }
            for item in report["results"]
        ]
        st.dataframe(rows, use_container_width=True)
        show_json(report)
