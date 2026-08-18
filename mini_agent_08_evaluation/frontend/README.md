# Mini Agent 08 · 공용 Frontend

하나의 Streamlit 화면에서 Python과 LangGraph Backend를 선택하고 01~08의 누적 기능을 확인합니다.

## 실행

두 Backend를 먼저 실행한 뒤 새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_08_evaluation
.\.venv\Scripts\python.exe -m streamlit run .\frontend\app.py
```

## 구조

```text
frontend
├─ app.py              메뉴와 이동
├─ core                API 요청·환경·상태·공통 UI
└─ app_pages           기능별 화면
```

Sidebar에서 Backend를 바꾸면 API 주소만 변경됩니다. 8-1~8-5는 Mock 기반 평가이며, 8-6 Provider 비교만 선택적으로 실제 LLM을 호출합니다.

```dotenv
PYTHON_AGENT_API_URL=http://127.0.0.1:8000
LANGGRAPH_AGENT_API_URL=http://127.0.0.1:8001
```

로그인·회원가입은 포함하지 않고 교육용 사용자 ID를 사용합니다. 실제 서비스에서는 인증된 사용자 ID로 교체해야 합니다.
