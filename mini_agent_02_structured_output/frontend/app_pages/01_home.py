import streamlit as st


st.title("🏠 Mini Agent 02")
st.info("01단계 기능을 유지하면서 Prompt와 Structured Output을 추가합니다.")

st.markdown(
    """
### 이번 단계의 연결 흐름

```text
Role · Instruction · Context · Constraint
→ Prompt
→ LLM이 JSON 생성
→ Pydantic 검증
→ 안전한 Python 객체
→ Frontend 표시
```

### 세 가지를 구분하세요

1. JSON/dict는 데이터를 표현하는 형식입니다.
2. Pydantic은 타입, 범위, 필드 계약을 검증합니다.
3. Structured Output은 LLM에게 Schema에 맞춰 생성하도록 요청하고 다시 검증합니다.

기본 Provider는 Mock이므로 API Key와 비용 없이 모든 02단계 메뉴를 확인할 수
있습니다. 이후 Gemini, GPT, Docker Ollama/Llama를 같은 Schema로 비교합니다.

LangChain, Tool, RAG, Memory, Agent Workflow와 로그인은 이후 단계에서 추가합니다.
"""
)
