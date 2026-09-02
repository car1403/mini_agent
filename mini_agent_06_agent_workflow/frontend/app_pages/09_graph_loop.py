import streamlit as st

from clients.learning_client import run_loop
from core.api_client import ApiClientError


st.title("6-6. 반복과 안전한 종료")
st.caption("검증에 실패하면 한 번 수정하고, 최대 횟수를 넘으면 실패로 종료합니다.")

budget = st.select_slider("전체 예산", options=[200000, 300000, 400000, 500000, 600000], value=400000)
max_iterations = st.slider("최대 수정 횟수", 0, 3, 1)

st.code("create_plan → finish | revise → create_plan | fail", language="text")
if st.button("반복 Graph 실행", type="primary"):
    try:
        result = run_loop(budget, max_iterations)
        st.write("Trace:", " → ".join(result["trace"]))
        st.json(result)
    except ApiClientError as error:
        st.error(str(error))
