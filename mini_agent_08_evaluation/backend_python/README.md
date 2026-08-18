# Mini Agent 08 · Python Backend

조건문과 일반 Python 함수 호출로 Agent 흐름을 구현한 FastAPI Backend입니다. 01~08의 Tool·RAG·Memory·승인·평가 기능이 누적되어 있습니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_08_evaluation\backend_python
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

## Agent 흐름

```text
요청 분석 → 입력 검증 → Memory 조회 → 정책 검색
→ 일정 생성 → 승인 대기 → 승인 또는 거절
```

분기와 승인 상태는 `app/services/travel_service.py`가 관리하고, 규칙 평가는 `app/services/evaluation_service.py`가 담당합니다.

## 주요 API

| Method | Path | 기능 |
|---|---|---|
| GET | `/health` | Python Backend 상태 |
| POST | `/api/providers/travel-plan` | 구조화된 여행 일정 |
| POST | `/api/tools/select` | Tool 선택 |
| POST | `/api/tools/run` | 허용된 Mock Tool 실행 |
| POST | `/api/knowledge/search` | 정책 문서 검색 |
| GET/POST/DELETE | `/api/users/{user_id}/memories` | Memory 관리 |
| POST | `/api/agent/runs` | Python Agent 실행 |
| POST | `/api/agent/runs/{run_id}/approve` | 본인 승인 |
| POST | `/api/agent/runs/{run_id}/reject` | 본인 거절 |
| POST | `/api/evaluations/run` | 반복 가능한 규칙 평가 |
