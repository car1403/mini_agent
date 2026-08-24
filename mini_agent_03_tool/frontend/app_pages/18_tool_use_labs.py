"""7개 Lab의 Routing, Agent/Workflow, Tool, Trace를 한 화면에서 비교합니다.

Frontend는 업무 정책이나 Tool을 실행하지 않습니다. 사용자의 명시적 Lab 선택 또는
Ollama 자동 분류 요청을 Backend에 전달하고, 상태 변경 시 pending action ID를 다시
보내는 확인 UI 역할만 담당합니다.
"""

import uuid
import streamlit as st
from clients.agent_client import reset_labs, run_lab
from core.api_client import BackendAPIError

st.title("🧪 Tool Use 통합 Labs")
st.caption("Ollama 라우팅 → Backend Allowlist → Agent 또는 결정적 Workflow → Mock Repository")

if "lab_session_id" not in st.session_state:
    st.session_state.lab_session_id = str(uuid.uuid4())
if "lab_pending_actions" not in st.session_state:
    st.session_state.lab_pending_actions = {}

labels = {
    "auto": "Ollama 자동 선택", "parking": "주차장", "air_conditioner": "에어컨",
    "parcel_locker": "택배함", "cafe": "카페 주문", "library": "도서관",
    "inventory": "재고 예약", "travel": "여행 준비",
}
examples = {
    "auto": "오늘 부산 여행 준비를 도와줘", "parking": "차량 12가3456의 주차장 문을 열어줘",
    "air_conditioner": "현재 온도는 28도야", "parcel_locker": "L101 택배함을 인증번호 1234로 열어줘",
    "cafe": "라지 아메리카노 두 잔", "library": "M100 회원이 B101 도서를 대출하고 싶어",
    "inventory": "SKU-001 재고를 예약해 줘", "travel": "내일 부산 여행 준비물을 알려줘",
}
patterns = {
    "parking": ("Agent-assisted Workflow", "Agent는 차량 번호만 추출하고 Backend가 출입 권한과 문 열기 순서를 결정합니다."),
    "air_conditioner": ("Agent-assisted Workflow", "Agent는 온도만 추출하고 Backend 히스테리시스 규칙이 제어를 결정합니다."),
    "parcel_locker": ("Agent-assisted Workflow", "Agent는 입력만 추출하고 Backend가 인증·만료·재사용을 검사합니다."),
    "cafe": ("Agent-controlled Cycle", "Agent가 주문 상태를 유지하며 누락값 재질문 또는 Tool 실행 종료를 선택합니다."),
    "library": ("Agent-controlled Loop + Backend Workflow", "Agent가 필요한 조회 Tool을 선택하고 Backend가 Pending Action과 대출 정책을 통제합니다."),
    "inventory": ("Agent-assisted Workflow", "Agent는 예약값만 추출하고 Backend가 Version·수량을 재검증합니다."),
    "travel": ("Read-only Multi-Tool Agent", "Agent가 날짜에 맞는 날씨 Tool과 관광지 Tool을 실행하고 결과를 종합합니다."),
}

lab_id = st.selectbox("Lab 선택", list(labels), format_func=labels.get)
message = st.text_input("요청", value=examples[lab_id], key=f"lab_message_{lab_id}")

arguments = {}
with st.expander("구조화 arguments", expanded=lab_id not in ("auto", "cafe", "travel")):
    if lab_id == "parking": arguments["plate_number"] = st.text_input("차량 번호", "12가3456")
    elif lab_id == "air_conditioner": arguments["temperature_c"] = st.number_input("온도(°C)", value=28.0)
    elif lab_id == "parcel_locker":
        arguments["locker_id"] = st.text_input("택배함 ID", "L101"); arguments["code"] = st.text_input("인증 코드", "1234")
    elif lab_id == "library":
        arguments["member_id"] = st.text_input("회원 ID", "M100"); arguments["book_id"] = st.text_input("도서 ID", "B101")
    elif lab_id == "inventory":
        arguments["sku"] = st.text_input("SKU", "SKU-001"); arguments["quantity"] = st.number_input("수량", min_value=1, value=2); arguments["expected_version"] = st.number_input("조회 Version", min_value=1, value=1)

confirmed = st.checkbox("상태 변경 작업 실행 확인")
left, right = st.columns(2)
run_clicked = left.button("Lab 실행", type="primary", use_container_width=True)
if right.button("모든 Mock 상태 초기화", use_container_width=True):
    try:
        st.session_state.lab_pending_actions = {}
        st.success(reset_labs()["note"])
    except BackendAPIError as error: st.error(str(error))

if run_clicked:
    try:
        # 확인 단계에서는 Backend가 발급한 action ID를 전달합니다. 화면의 arguments를
        # 다시 신뢰하지 않으며 Backend도 저장된 검증값만 실행합니다.
        pending_action_id = st.session_state.lab_pending_actions.get(lab_id) if confirmed else None
        result = run_lab(message, st.session_state.lab_session_id, lab_id, arguments, confirmed, pending_action_id)
        if result["status"] == "confirmation_required" and result["state"].get("pending_action_id"):
            st.session_state.lab_pending_actions[lab_id] = result["state"]["pending_action_id"]
        elif result["status"] in ("completed", "rejected", "error"):
            st.session_state.lab_pending_actions.pop(lab_id, None)
        if result["status"] == "completed": st.success(result["final_answer"])
        elif result["status"] == "confirmation_required": st.warning(result["final_answer"])
        else: st.info(result["final_answer"])
        a, b = st.columns(2)
        with a:
            pattern, rationale = patterns.get(
                result["lab_id"],
                ("Routing clarification", "Lab을 확정하지 못해 Tool이나 상태 변경을 실행하지 않았습니다."),
            )
            st.subheader("실행 유형")
            st.code(f"{result['execution_type']} · {pattern}")
            st.caption(rationale)
            st.subheader("Routing"); st.json(result["routing"])
            st.subheader("Tool Calls"); st.json(result["tool_calls"])
        with b:
            st.subheader("현재 상태"); st.json(result["state"])
            st.subheader("종료 이유"); st.code(result["termination_reason"])
        with st.expander("전체 Trace", expanded=True): st.json(result["trace"])
    except BackendAPIError as error: st.error(str(error))
