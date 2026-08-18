import streamlit as st


st.title("🏠 Mini Agent 01")
st.info("단위 Python 판단을 FastAPI와 Streamlit 메뉴로 하나씩 연결합니다.")

st.markdown(
    """
### 메뉴 누적 순서

1. LLM·Workflow·Agent 비교
2. 여행 요청 분류와 추가 질문
3. Mock으로 Frontend·Backend 연결 확인
4. 이전 과정의 Gemini 연결
5. OpenAI GPT 연결
6. Docker Ollama/Llama 연결
7. Provider별 응답·지연·실패 비교

### 아직 추가하지 않는 기능

Structured Output, LangChain, Tool, RAG, Memory, Agent, LangGraph, 로그인은
이후 단계에서 하나씩 추가합니다.

이미지 분석과 TTS의 서비스 연결은 Structured Output을 학습한 뒤
`mini_agent_01_llm`에서 진행합니다.
"""
)
