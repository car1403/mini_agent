import streamlit as st

from core.state import current_agent_run, save_agent_run, selected_backend
from core.ui import backend_request, run_api


backend_name, _ = selected_backend()
st.title("7-5. 승인과 거절")
st.caption(f"현재 선택: {backend_name}")

user_id = st.text_input("사용자 ID", "demo-user")
message = st.text_area(
    "요청",
    "8월 부산 2박 여행을 성인 2명이 가고 싶어요. 예산은 50만 원입니다.",
)

if st.button("Agent 실행"):
    save_agent_run(
        run_api(
            lambda: backend_request(
                "POST",
                "/api/agent/runs",
                {"user_id": user_id, "message": message},
            )
        )
    )

run = current_agent_run()
if run:
    st.info(
        f"Backend: {backend_name} · 상태: {run['status']} · "
        f"현재 단계: {run['current_node']}"
    )
    st.write(run.get("message", ""))
    if run.get("result"):
        st.json(run["result"])
    if run.get("trace"):
        st.subheader("실행 Trace")
        st.dataframe(run["trace"], use_container_width=True)
    if run.get("requires_approval"):
        st.warning("교육용 Mock 예약 요청이며 실제 예약은 발생하지 않습니다.")
        approve, reject = st.columns(2)
        if approve.button("승인"):
            save_agent_run(
                run_api(
                    lambda: backend_request(
                        "POST",
                        f"/api/agent/runs/{run['run_id']}/approve",
                        {"actor": user_id, "note": "Streamlit 승인"},
                    )
                )
            )
            st.rerun()
        if reject.button("거절"):
            save_agent_run(
                run_api(
                    lambda: backend_request(
                        "POST",
                        f"/api/agent/runs/{run['run_id']}/reject",
                        {"actor": user_id, "note": "Streamlit 거절"},
                    )
                )
            )
            st.rerun()
