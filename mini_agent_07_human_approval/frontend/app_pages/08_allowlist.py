import streamlit as st


st.title("7-2. Allowlist와 소유권")
st.caption("LLM의 제안과 시스템의 실행 권한을 분리합니다.")

allowed_actions = {"search_policy", "create_draft", "send_message"}
action = st.selectbox("LLM이 제안한 작업", ["search_policy", "send_message", "make_payment"])
request_user = st.text_input("요청 사용자", "user-a")
resource_owner = st.text_input("데이터 소유자", "user-a")

if st.button("정책 검사", type="primary"):
    if action not in allowed_actions:
        st.error("차단: allowlist에 없는 작업입니다.")
    elif request_user != resource_owner:
        st.error("차단: 다른 사용자의 데이터입니다.")
    else:
        st.success("정책 검사를 통과했습니다.")

st.info("Prompt에 '승인 없이 실행하라'고 적혀 있어도 코드의 정책은 바뀌지 않습니다.")
