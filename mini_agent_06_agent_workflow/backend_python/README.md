# Mini Agent 06 · Python Backend

조건문과 일반 Python 함수 호출로 Agent 흐름을 구현한 초보자용 FastAPI
Backend입니다. LangGraph를 사용하지 않으므로 각 단계가 호출되는 순서를 코드에서
직접 따라갈 수 있습니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_06_langgraph\backend_python
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

## Agent 흐름

```text
요청 분석 → 입력 검증 → Memory 조회 → 정책 검색
→ 일정 생성 → 승인 대기 → 승인 또는 거절
```

분기와 승인 상태는 `app/services/travel_service.py`의 일반 Python 코드가
관리합니다. Agent 요청에는 `engine` 값을 보내지 않습니다.

## 공통 API

| Method | Path | 기능 |
| --- | --- | --- |
| GET | `/health` | `agent_type=python` 확인 |
| GET | `/api/providers/status` | LLM Provider 설정 상태 |
| POST | `/api/providers/generate` | 일반 LLM 호출 |
| POST | `/api/providers/travel-plan` | 구조화된 여행 일정 |
| POST | `/api/travel/extract` | 여행 요청 구조화 |
| POST | `/api/tools/select` | Tool 선택 |
| POST | `/api/tools/run` | 허용된 Mock Tool 실행 |
| POST | `/api/knowledge/search` | 정책 문서 검색 |
| GET/POST/DELETE | `/api/users/{user_id}/memories` | Memory 관리 |
| POST | `/api/agent/runs` | Python Agent 실행 |
| POST | `/api/agent/runs/{run_id}/approve` | 직접 구현한 승인 처리 |
| POST | `/api/agent/runs/{run_id}/reject` | 직접 구현한 거절 처리 |
