import streamlit as st

from clients.agent_client import get_health, get_providers
from core.api_client import BACKEND_URL, BackendAPIError


st.title("🩺 환경 상태")
st.caption(f"Backend: {BACKEND_URL}")
if st.button("연결 상태 확인"):
    try:
        st.json(get_health())
        st.dataframe(get_providers()["providers"], use_container_width=True)
    except BackendAPIError as error:
        st.error(str(error))
