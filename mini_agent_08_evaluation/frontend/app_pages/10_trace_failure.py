import streamlit as st

from core.ui import backend_request, run_api


st.title("8-4. Trace 실패 찾기")
st.caption("의도적으로 실패하는 시나리오에서 첫 실패 검사를 찾습니다.")

if st.button("실패 시나리오 실행", type="primary"):
    report = run_api(
        lambda: backend_request(
            "POST",
            "/api/evaluations/run",
            {
                "scenarios": [
                    {
                        "name": "잘못된 기대 Tool",
                        "message": "안녕하세요",
                        "expected_tool": "get_weather",
                        "expected_status": "completed",
                    }
                ]
            },
        )
    )
    if report:
        result = report["results"][0]
        st.dataframe(result["trace"], use_container_width=True)
        failed = next(event for event in result["trace"] if event["status"] == "failed")
        st.error(f"첫 실패 단계: {failed['node']} · 원인: {failed['error']}")
        st.write("실패한 검사:", result["failed_checks"])
