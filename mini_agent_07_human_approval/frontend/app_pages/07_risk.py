import streamlit as st


st.title("7-1. 작업 위험도")
st.caption("작업이 데이터를 읽기만 하는지, 외부 상태를 변경하는지 구분합니다.")

risks = {
    "정책 검색": ("read", "자동 허용"),
    "메시지 초안": ("draft", "자동 허용"),
    "메시지 전송": ("change", "승인 필요"),
    "실제 결제": ("forbidden", "교육 과정에서 금지"),
}
action = st.selectbox("작업", list(risks))
risk, policy = risks[action]
st.json({"action": action, "risk": risk, "policy": policy})
