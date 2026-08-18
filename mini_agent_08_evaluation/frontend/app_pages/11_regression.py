import streamlit as st

from core.ui import backend_request, run_api


st.title("8-5. 회귀 테스트")
st.caption("수정 전 기준 결과를 저장하고 현재 결과와 다시 비교합니다.")

left, right = st.columns(2)
if left.button("현재 결과를 기준으로 저장"):
    report = run_api(lambda: backend_request("POST", "/api/evaluations/run", {}))
    if report:
        st.session_state.evaluation_baseline = report
        st.success("기준 결과를 저장했습니다.")

if right.button("다시 실행하여 비교", type="primary"):
    baseline = st.session_state.get("evaluation_baseline")
    if not baseline:
        st.error("먼저 기준 결과를 저장하세요.")
    else:
        current = run_api(lambda: backend_request("POST", "/api/evaluations/run", {}))
        if current:
            before = {item["scenario"]: item["passed"] for item in baseline["results"]}
            after = {item["scenario"]: item["passed"] for item in current["results"]}
            rows = [
                {
                    "시나리오": name,
                    "기준": passed,
                    "현재": after.get(name, False),
                    "회귀": passed and not after.get(name, False),
                }
                for name, passed in before.items()
            ]
            st.dataframe(rows, use_container_width=True)
            regressions = [row for row in rows if row["회귀"]]
            if regressions:
                st.error(f"회귀 {len(regressions)}개를 발견했습니다.")
            else:
                st.success("새로운 회귀가 없습니다.")

st.info("수업에서는 기준 저장 후 Backend의 Tool 선택 규칙 하나를 바꾸고 다시 실행해 봅니다.")
