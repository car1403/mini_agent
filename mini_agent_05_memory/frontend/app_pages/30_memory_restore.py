import streamlit as st

from clients.agent_client import (
    append_conversation, export_memory, patch_session, restore_memory,
    save_session,
)
from core.api_client import BackendAPIError


st.title("5-7. Hybrid Memory 복원")
st.caption("Redis 단기 상태와 PostgreSQL 장기 Memory·대화를 사용자별로 결합합니다.")

user_id = st.text_input("user_id", "user-a")
session_id = st.text_input("session_id", "hybrid-demo")

if st.button("예제 Session과 대화 저장"):
    try:
        st.json(save_session(session_id, {"step": "collect_information"}, user_id))
        append_conversation(user_id, session_id, "user", "조용한 호텔을 찾고 있어요.")
        st.success("Redis Session과 PostgreSQL 대화를 저장했습니다.")
    except BackendAPIError as error:
        st.error(str(error))

if st.button("Session 원자 갱신"):
    try:
        st.json(patch_session(user_id, session_id, {"destination": "부산"}, 0))
    except BackendAPIError as error:
        st.error(str(error))

if st.button("Hybrid 복원", type="primary"):
    try:
        result = restore_memory(user_id, session_id)
        st.json(result)
        with st.expander("복원 Trace", expanded=True):
            st.json(result["trace"])
    except BackendAPIError as error:
        st.error(str(error))

if st.button("장기 Memory 내보내기"):
    try:
        st.json(export_memory(user_id))
    except BackendAPIError as error:
        st.error(str(error))
