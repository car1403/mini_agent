import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Mini Agent 07 · Safe Order Agent", page_icon="🛡️", layout="wide")
st.title("Mini Agent 07 · Safe Order Agent")
st.caption("상품 조회는 자동 실행하고 실제 주문 생성은 승인 Snapshot을 확인한 뒤 한 번만 실행합니다.")


def get(path: str):
    response = requests.get(f"{API_BASE_URL}{path}", timeout=5)
    response.raise_for_status()
    return response.json()


def post(path: str, payload: dict):
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


try:
    mcp = get("/api/agents/mcp-status")
except requests.RequestException:
    st.warning("Order MCP Tool Server에 연결할 수 없습니다. 8010 포트의 Server를 먼저 실행하세요.")
else:
    st.success(f"MCP 연결: {mcp['status']} · Tool {mcp['tool_count']}개")

with st.expander("Safe Order Agent의 실행 경계", expanded=True):
    st.markdown(
        """
| Tool | 위험도 | 실행 방식 |
| --- | --- | --- |
| `search_product` | read | 자동 실행 |
| `check_inventory` | read | 자동 실행 |
| `calculate_order_total` | read | 자동 실행 |
| `place_order` | change | 사용자 승인 후 실행 |
"""
    )

actor_id = st.text_input("현재 사용자 ID", "user-01")
question = st.text_area("주문 요청", "무선 키보드 2개의 재고와 금액을 확인해서 주문해 줘.", height=100)

if "run_result" not in st.session_state:
    st.session_state.run_result = None

if st.button("안전 Order Agent 실행", type="primary", use_container_width=True):
    try:
        st.session_state.run_result = post(
            "/api/agents/runs",
            {"actor_id": actor_id, "question": question},
        )
    except requests.RequestException as error:
        st.error(f"Agent 실행 실패: {error}")

result = st.session_state.run_result
if result:
    @st.fragment(run_every="1s")
    def render_live_progress(run_id: str):
        try:
            progress_data = get(f"/api/agents/runs/{run_id}/progress")
        except requests.RequestException:
            return
        live = progress_data.get("state", {})
        percent = int(live.get("progress", 0))
        st.progress(percent, text=live.get("message", "진행 상태를 확인하고 있습니다."))
        with st.expander("실시간 실행 Timeline", expanded=True):
            for event in progress_data.get("events", []):
                st.write(f"{event.get('created_at', '')} · {event.get('message', event.get('stage'))}")

    render_live_progress(result["run_id"])
    if result["status"] == "waiting_approval":
        pending = result["pending_approval"]
        target = pending["approval_target"]
        arguments = target["arguments"]
        st.warning("읽기와 계산이 끝났습니다. 아래 주문 내용을 확인하세요.")
        st.markdown("### 주문 승인 Snapshot")
        col1, col2, col3 = st.columns(3)
        col1.metric("실행 Tool", target["tool"])
        col2.metric("상품 ID", arguments.get("product_id", "-"))
        col3.metric("수량", arguments.get("quantity", "-"))
        st.json(target)

        note = st.text_input("승인·거절 메모", key=f"note_{result['run_id']}")
        approve_col, reject_col = st.columns(2)

        def decide(decision: str):
            return post(
                f"/api/agents/runs/{result['run_id']}/decision",
                {
                    "actor_id": actor_id,
                    "decision": decision,
                    "approval_target": target,
                    "note": note,
                },
            )

        if approve_col.button("승인 후 주문 생성", type="primary", use_container_width=True):
            try:
                st.session_state.run_result = decide("approve")
                st.rerun()
            except requests.RequestException as error:
                st.error(f"승인 처리 실패: {error}")
        if reject_col.button("주문 거절", use_container_width=True):
            try:
                st.session_state.run_result = decide("reject")
                st.rerun()
            except requests.RequestException as error:
                st.error(f"거절 처리 실패: {error}")
    elif result["status"] == "completed":
        st.success(result.get("answer") or "승인된 주문이 생성되었습니다.")
    elif result["status"] == "rejected":
        st.info("사용자가 주문 생성을 거절했습니다.")
    else:
        st.error(f"실행 종료: {result['termination_reason']}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("상태", result["status"])
    col2.metric("종료 이유", result["termination_reason"])
    col3.metric("LLM 호출", result["llm_calls"])
    col4.metric("MCP Tool 호출", result["tool_calls"])

    st.subheader("Agent·Policy·Approval Trace")
    for index, item in enumerate(result["trace"], start=1):
        with st.expander(f"{index}. {item.get('owner', 'system')} · {item.get('stage', 'unknown')}"):
            st.json(item)

    try:
        audit = get(f"/api/agents/runs/{result['run_id']}/audit")
    except requests.RequestException:
        pass
    else:
        with st.expander("Audit Log"):
            st.json(audit)

st.divider()
st.info("Travel의 일정 저장과 Support의 반품 요청도 같은 승인 패턴을 적용할 수 있습니다. 이 프로젝트는 주문 하나에 집중합니다.")
