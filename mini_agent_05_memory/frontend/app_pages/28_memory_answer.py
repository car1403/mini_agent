import streamlit as st

from clients.agent_client import personalize_with_memory
from core.api_client import BackendAPIError


st.title("5-5. 관련 Memory와 개인화 답변")
st.caption("질문과 관련된 Memory만 선택해 Prompt에 넣습니다.")

storage = "postgres"
st.caption("장기 Memory 저장소: PostgreSQL")
user_id = st.selectbox("사용자", ["student-01", "student-02"])
question = st.selectbox(
    "질문",
    [
        "부산에서 이동 경로를 추천해줘",
        "부산에서 식당을 추천해줘",
        "조용한 숙소를 추천해줘",
        "부산 날씨를 알려줘",
    ],
)
provider = st.selectbox("답변 Provider", ["openai", "gemini", "ollama"])

st.info("먼저 Memory CRUD 메뉴에서 현재 사용자의 선호를 저장하세요.")
if st.button("개인화 답변 만들기", type="primary"):
    try:
        result = personalize_with_memory(user_id, question, storage, provider)
        st.subheader("선택된 Memory")
        st.json(result["used_memories"])
        st.subheader("최종 답변")
        if result["used_memories"]:
            st.success(result["answer"])
        else:
            st.warning(result["answer"])
    except BackendAPIError as error:
        st.error(str(error))
