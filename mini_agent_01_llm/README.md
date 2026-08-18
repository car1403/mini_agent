# Mini Agent 01 · LLM 판단에서 서비스 연결까지

`01_llm-to-agent`의 단위 Python 예제를 FastAPI Endpoint와 Streamlit 메뉴로
하나씩 연결합니다. 첫 단계에서는 로그인과 Agent Workflow를 넣지 않습니다.

```text
Python 판단 함수
→ FastAPI
→ Streamlit 메뉴
→ Mock
→ Gemini
→ OpenAI GPT
→ Docker Ollama/Llama
→ 이미지 분석
→ 음성 생성
```

## 이번 단계에서 구현

- LLM·Workflow·Agent 비교
- 여행 요청 분류
- 낮은 confidence와 추가 질문
- Mock Provider로 연결 확인
- Gemini·GPT·Ollama/Llama 선택
- 동일 Prompt의 모델·응답 시간·실패 비교
- GPT 이미지 분석과 업로드 검증
- 여행 안내문 MP3 합성 음성 생성

## 아직 구현하지 않음

- Structured Output
- LangChain
- Tool
- RAG와 Memory
- Agent Workflow와 LangGraph
- 로그인

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_01_llm
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

터미널 1:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

터미널 2:

```powershell
cd C:\mini_agent_st\mini_agent_01_llm
streamlit run .\frontend\app.py
```

Ollama는 `C:\mini_agent_st\infra`에서 먼저 실행하고 모델을 내려받아야 합니다.
Cloud Provider는 `.env`에 해당 API Key와 모델을 설정한 경우에만 호출합니다.

## 확인 순서

1. LLM·Workflow·Agent 메뉴에서 두 판단 결과를 비교합니다.
2. 여행 요청 분류에서 `confidence`와 추가 질문을 확인합니다.
3. 환경 상태에서 Backend와 Provider 설정을 확인합니다.
4. 기본 Provider인 Mock으로 Frontend·Backend 연결을 확인합니다.
5. 이전 과정에서 사용한 Gemini를 연결합니다.
6. GPT와 Ollama/Llama를 추가해 같은 질문을 비교합니다.
7. Ollama Container를 중지하고 실패가 비교 결과에 남는지 확인합니다.
8. 이미지 분석에서 업로드 형식과 구조화된 결과를 확인합니다.
9. 음성 생성에서 안내문을 MP3로 변환하고 합성 음성 고지를 확인합니다.

Provider 비교는 `Gemini → GPT → Ollama/Llama` 순서로 진행합니다. Cloud Provider는
호출량과 비용을 확인하고, Ollama는 Docker와 모델 준비 상태를 먼저 확인합니다.

이미지 분석과 음성 생성은 01 단원의 `1-5`, `1-6` 메뉴에서 진행합니다.
