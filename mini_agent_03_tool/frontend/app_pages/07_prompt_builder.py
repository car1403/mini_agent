import streamlit as st

from clients.agent_client import preview_prompt
from core.api_client import BackendAPIError


st.title("🧩 Prompt 구성")
role = st.text_input("Role", "여행 요청 분석가")
instruction = st.text_area("Instruction", "필요한 정보를 추출하세요.")
context = st.text_area("Context", "사용자는 국내 여행을 계획합니다.")
constraint = st.text_area("Constraint", "추측하지 마세요.")
if st.button("Prompt 조립"):
    try:
        st.code(preview_prompt(role, instruction, context, constraint)["prompt"], language="text")
    except BackendAPIError as error:
        st.error(str(error))
