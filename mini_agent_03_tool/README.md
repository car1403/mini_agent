# Mini Agent 03 · Tool Use

01~03에서 만든 화면과 API를 유지하면서 Tool 선택, 안전 실행, 최종 답변 생성을 추가한 누적형 완성본입니다.

```text
Streamlit app_pages
  → clients/agent_client.py
  → FastAPI routers/agent_router.py
  → providers.py에서 Tool 선택
  → tools/travel_tools.py에서 검증·실행
  → Tool Result로 최종 답변
```

## 새로 배우는 내용

- Python 함수·Tool Schema·Tool Call·Tool Result
- Pydantic arguments 검증
- Tool 선택과 실행 분리
- Allowlist 기반 안전 실행
- 공통 Tool 오류 코드
- Tool Result를 사용한 최종 답변
- Mock·Gemini·GPT·Ollama/Llama 비교

## 추가 메뉴

1. `Tool 선택`: 등록된 Schema와 LLM의 Tool Call 제안을 확인합니다.
2. `Tool 실행`: arguments를 수정하고 Backend 검증 결과를 확인합니다.
3. `Agent Loop`: 선택 → 실행 → Tool Result → 최종 답변을 한 화면에서 추적합니다.

실행되는 Tool은 날씨·숙소·관광지 조회용 Mock 함수뿐입니다. 실제 예약, 결제, 환불, 삭제는 실행하지 않습니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

기본 Provider는 Mock입니다. 먼저 Mock으로 전체 Agent Loop를 확인한 다음 준비된 Provider만 선택적으로 비교합니다.
