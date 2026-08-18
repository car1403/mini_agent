import streamlit as st


st.title("7-6. 안전한 실행")
st.caption("변경 작업은 interrupt 이후에 두고 중복 실행을 막습니다.")

st.code(
    "prepare_draft()          # 변경 없음\n"
    "decision = interrupt(...)\n"
    "validate(decision)       # 승인 값 검증\n"
    "execute_once(run_id)     # 승인 후 한 번만 Mock 실행",
    language="python",
)

checks = {
    "승인 대기 상태인가": True,
    "승인자가 실행 소유자인가": True,
    "같은 run_id가 이미 처리됐는가": False,
    "실제 결제 Tool인가": False,
}
st.json(checks)
st.info("현재 actor와 user_id는 교육용 값입니다. 실제 서비스는 로그인 토큰으로 신원을 확인합니다.")
