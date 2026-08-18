import streamlit as st

from clients.agent_client import get_health, get_providers
from core.api_client import BACKEND_URL, BackendAPIError


st.title("🩺 환경 상태")
st.caption(f"Backend: {BACKEND_URL}")

if st.button("연결 상태 확인"):
    try:
        health = get_health()
        providers = get_providers()
        st.subheader("Backend")
        st.json(health)
        st.subheader("Provider")
        st.dataframe(providers["providers"], use_container_width=True)
        st.caption("configured는 설정 여부이며 API Key 값은 화면에 노출하지 않습니다.")
    except BackendAPIError as error:
        st.error(str(error))
