import streamlit as st


st.title("3-5. Tool 오류 처리")
st.caption("Tool 실패를 숨기지 않고 다음 행동을 결정할 수 있는 결과로 바꿉니다.")

scenario = st.radio("실행 상황", ["정상", "시간 초과", "허용되지 않은 Tool"])
if st.button("Mock Tool 실행", type="primary"):
    if scenario == "정상":
        st.json({"status": "success", "data": {"temperature": 24}})
    elif scenario == "시간 초과":
        st.json({"status": "error", "retryable": True, "message": "응답 시간이 초과되었습니다."})
    else:
        st.json({"status": "blocked", "retryable": False, "message": "allowlist에 없는 Tool입니다."})

st.info("재시도 가능한 오류와 정책상 차단된 오류를 구분합니다.")
