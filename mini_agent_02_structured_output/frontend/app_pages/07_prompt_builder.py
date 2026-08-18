import streamlit as st

from clients.agent_client import preview_prompt
from core.api_client import BackendAPIError


st.title("🧩 Prompt 구성")
st.caption("한 문장에 섞어 쓰지 않고 역할, 지시, 맥락, 제약을 나눠 확인합니다.")
role = st.text_input("Role", "당신은 초보자를 돕는 여행 요청 분석가입니다.")
instruction = st.text_area("Instruction", "사용자의 여행 요청에서 필요한 정보를 추출하세요.")
context = st.text_area("Context", "사용자는 국내 여행을 계획하고 있습니다.")
constraint = st.text_area("Constraint", "추측하지 말고 모르는 값은 누락 정보로 표시하세요.")

if st.button("Prompt 조립"):
    try:
        result = preview_prompt(role, instruction, context, constraint)
        st.code(result["prompt"], language="text")
    except BackendAPIError as error:
        st.error(str(error))
