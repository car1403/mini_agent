import streamlit as st


st.title("🏠 Mini Agent 05 · Memory")
st.write("01~05단계 기능을 유지하면서 대화 Window, 단기 상태, 장기 사용자 Memory를 추가합니다.")

st.code(
    "질문 → 관련 Memory 선택 → Prompt에 추가 → 개인화 답변\n"
    "사용자 → 내 Memory 확인·수정·삭제",
    language="text",
)

st.info("처음에는 Mock 저장소로 시작하세요. Docker 없이 사용자 격리·CRUD·개인화 답변을 확인할 수 있습니다.")

st.warning("비밀번호, 카드번호, 여권번호, API Key 같은 민감정보는 Memory에 저장하지 않습니다.")
