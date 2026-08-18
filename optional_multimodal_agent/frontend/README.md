# 11 공용 Agent Frontend

하나의 Streamlit 화면에서 Python Agent Backend와 LangGraph Agent Backend를
선택하고 동일한 요청으로 결과와 Trace를 비교합니다.

`app_pages/08_multimodal.py`에서는 선택한 백엔드에 연결하여 GPT 이미지
분석과 TTS를 실습합니다. 이 기능은 OpenAI 전용 선택 확장이므로 일반
Provider 비교 학습과 분리되어 있습니다.

`C:\mini_frontend_sam\mini_frontend`와 같은 초보자용 멀티페이지 패턴을
사용합니다. `app.py`는 메뉴와 이동을 담당하고 실제 화면은 `app_pages`에
기능별로 분리합니다.

```text
frontend
├─ app.py
├─ core
│  ├─ config.py
│  ├─ api_client.py
│  ├─ state.py
│  └─ ui.py
└─ app_pages
   ├─ 01_home.py
   ├─ 02_environment.py
   ├─ 03_llm.py
   ├─ 04_tool.py
   ├─ 05_knowledge_memory.py
   └─ 06_agent.py
   └─ 07_evaluation.py
```

로그인·회원가입은 포함하지 않으며 교육용 `demo-user`를 사용합니다.

## core의 역할

| 파일 | 담당 내용 |
| --- | --- |
| `config.py` | 환경 변수와 두 Backend 주소 |
| `api_client.py` | HTTP 요청과 오류 변환 |
| `state.py` | Backend 선택 및 Agent 실행 상태 |
| `ui.py` | 공통 Sidebar, Spinner, JSON 표시 |

페이지 파일은 입력·버튼·결과 표시에 집중하고 재사용 로직은 `core`에 둡니다.

Sidebar의 LLM Provider 선택은 LLM·Tool·Agent 화면에서 공통으로 사용합니다.
평가 화면은 선택한 여러 Provider에 동일한 Tool 시나리오를 실행합니다.

## Backend 실행

터미널 1:

```powershell
cd C:\mini_agent_st\optional_multimodal_agent\backend_python
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

터미널 2:

```powershell
cd C:\mini_agent_st\optional_multimodal_agent\backend_langgraph
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

터미널 3:

```powershell
cd C:\mini_agent_st\optional_multimodal_agent
.\.venv\Scripts\python.exe -m streamlit run .\frontend\app.py
```

## 연결 주소

```dotenv
PYTHON_AGENT_API_URL=http://127.0.0.1:8000
LANGGRAPH_AGENT_API_URL=http://127.0.0.1:8001
```

Frontend는 Sidebar에서 선택한 Backend 주소만 변경합니다. API Key와 실행 엔진
변수는 전송하지 않으며, 두 Backend는 동일한 API 계약을 제공합니다.

Sidebar에서는 Backend와 LLM Provider를 별도로 선택합니다. Provider 선택은
LLM·Tool·Agent 화면에 공통 적용되고, Backend 또는 Provider를 바꾸면 이전
Agent 실행 상태를 표시하지 않습니다.
