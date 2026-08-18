import streamlit as st

from core.state import selected_backend


backend_name, backend_url = selected_backend()

st.title("🏠 여행 Agent 학습")
st.info("왼쪽 메뉴에서 학습할 기능을 선택하세요.")
st.write("일반 Python Workflow와 LangGraph Workflow를 같은 화면에서 비교합니다.")

col1, col2 = st.columns(2)
col1.metric("현재 Backend", backend_name)
col2.metric("연결 주소", backend_url)

st.markdown(
    """
### 추천 학습 순서

1. 환경 상태에서 Backend 연결을 확인합니다.
2. LLM과 구조화에서 Provider별 결과를 비교합니다.
3. Tool에서 선택과 실행을 구분합니다.
4. RAG와 Memory에서 외부 지식과 사용자 기억을 확인합니다.
5. 작업 위험도와 Tool allowlist를 확인합니다.
6. 중단·저장·재개와 LangGraph interrupt를 비교합니다.
7. 승인·거절 후 Mock 작업이 한 번만 실행되는지 확인합니다.
"""
)
