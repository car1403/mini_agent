import streamlit as st


st.title("8-1. 평가가 필요한 이유")
st.caption("프로그램이 끝까지 실행됐어도 Agent 행동은 틀릴 수 있습니다.")

st.code(
    "사용자: 부산 여행을 준비해줘\n"
    "기대: 정보가 부족하므로 질문하기\n"
    "실제: 임의로 호텔 Tool 실행하기",
    language="text",
)

left, right = st.columns(2)
left.success("프로그램 실행: 성공")
right.error("Agent 행동 평가: 실패")

st.info("처음에는 Tool과 상태만 비교합니다. 점수보다 실패 이유를 찾는 것이 중요합니다.")
