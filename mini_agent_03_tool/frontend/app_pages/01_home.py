import streamlit as st


st.title("🏠 Mini Agent 03 · Tool Use")
st.info("이전 메뉴를 유지하면서 Tool 선택과 Backend 실행을 분리합니다.")
st.markdown("""
```text
사용자 요청
→ LLM이 Tool Call 제안
→ Backend가 Allowlist 확인
→ Pydantic arguments 검증
→ 조회용 Mock 함수 실행
→ Tool Result
```

LLM이 Tool을 선택해도 함수가 자동 실행되는 것은 아닙니다. 이 단계에서는 날씨,
숙소, 관광지 조회용 Mock Tool만 사용하며 예약·결제·삭제는 실행하지 않습니다.
""")
