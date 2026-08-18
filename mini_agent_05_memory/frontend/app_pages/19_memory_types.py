import streamlit as st

from clients.agent_client import get_memory_types
from core.api_client import BackendAPIError


st.title("1️⃣ Memory 종류")
st.caption("대화 기록·단기 상태·장기 Memory·RAG 문서를 먼저 구분합니다.")

try:
    result = get_memory_types()
    st.dataframe(result["types"], use_container_width=True)
    left, right = st.columns(2)
    with left:
        st.success("저장 허용 key")
        st.write(result["allowed_keys"])
    with right:
        st.error("저장 차단 예시")
        st.write(result["blocked_examples"])
except BackendAPIError as error:
    st.error(str(error))

st.info("RAG는 외부 지식을 찾고, Memory는 사용자와 현재 작업의 상태를 기억합니다.")
