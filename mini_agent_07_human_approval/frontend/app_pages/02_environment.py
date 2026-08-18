import streamlit as st

from core.state import selected_backend
from core.ui import backend_request, run_api


backend_name, _ = selected_backend()
st.title("🩺 환경 상태")
st.caption(f"현재 선택: {backend_name}")

if st.button("상태 새로고침"):
    health = run_api(lambda: backend_request("GET", "/health"))
    providers = run_api(lambda: backend_request("GET", "/api/providers/status"))
    if health:
        st.subheader("Backend")
        st.json(health)
    if providers:
        st.subheader("LLM Provider")
        st.dataframe(providers["providers"], use_container_width=True)
        st.caption("configured는 설정 여부이며 실제 유료 API를 호출하지 않습니다.")
