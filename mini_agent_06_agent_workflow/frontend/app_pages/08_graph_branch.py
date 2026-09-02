import streamlit as st

from clients.learning_client import run_branch
from core.api_client import ApiClientError


st.title("6-3. 조건 분기")

examples = {
    "목적지 있음": "부산 여행을 준비해줘",
    "다른 목적지": "제주 여행을 준비해줘",
    "목적지 없음": "여행을 준비해줘",
}
case = st.selectbox("입력 유형", list(examples))
message = examples[case]
st.code(message, language="text")

expected = "extract → create_plan → END" if case != "목적지 없음" else "extract → ask_user → END"
st.write("예상 경로:", expected)

if st.button("Graph 실행", type="primary"):
    try:
        result = run_branch(message)
        st.write("실제 Trace:", " → ".join(result["trace"]))
        st.json(result)
    except ApiClientError as error:
        st.error(str(error))
