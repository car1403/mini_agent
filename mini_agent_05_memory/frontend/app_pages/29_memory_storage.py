import streamlit as st

from clients.agent_client import delete_session, get_memory_status, get_session, save_session
from core.api_client import BackendAPIError


st.title("5-6. Redis 단기 상태와 PostgreSQL 장기 Memory")
st.caption("Docker를 사용하는 마지막 실습입니다.")

st.code("cd C:\\mini_agent_st\\infra\ndocker compose up -d", language="powershell")

if st.button("저장소 연결 상태 확인"):
    try:
        st.json(get_memory_status())
    except BackendAPIError as error:
        st.error(str(error))

st.subheader("Redis Session 실습")
session_id = st.text_input("session_id", "travel-demo")
user_id = st.text_input("user_id", "demo-user")
state = {"current_step": "collect_information", "destination": "부산"}

left, middle, right = st.columns(3)
with left:
    if st.button("상태 저장"):
        try:
            st.json(save_session(session_id, state, user_id))
        except BackendAPIError as error:
            st.error(str(error))
with middle:
    if st.button("상태와 TTL 조회"):
        try:
            st.json(get_session(session_id, user_id))
        except BackendAPIError as error:
            st.error(str(error))
with right:
    if st.button("상태 삭제"):
        try:
            st.json(delete_session(session_id, user_id))
        except BackendAPIError as error:
            st.error(str(error))

st.info("장기 Memory는 이전 메뉴에서 storage를 postgres로 바꿔 저장·조회·삭제합니다.")
