# 09 Python Agent Backend

조건문과 일반 Python 함수 호출로 Agent 흐름을 구현한 초보자용 FastAPI
Backend입니다. LangGraph를 사용하지 않으므로 각 단계가 호출되는 순서를 코드에서
직접 따라갈 수 있습니다.

## 실행

Python Agent는 기본적으로 `http://127.0.0.1:8000`에서 실행합니다. 프로젝트 루트
`.env`의 `PYTHON_AGENT_API_URL`도 같은 주소를 사용해야 합니다.
Tool 선택과 실행에는 별도로 실행한 Travel Tools MCP Server
(`http://127.0.0.1:8020/mcp`)가 필요합니다.

```powershell
cd C:\mini_agent\optional_multimodal_agent\backend_python
..\.venv\Scripts\python.exe -m app.main
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
| POST | `/api/tools/select` | 선택한 Provider의 Tool Calling |
| GET | `/api/tools/status` | MCP Tool Server 연결 상태 |
| POST | `/api/tools/run` | MCP Tool Server의 허용된 Tool 실행 |
| POST | `/api/knowledge/search` | 정책 문서 검색 |
| GET/POST/DELETE | `/api/users/{user_id}/memories` | Memory 관리 |
| POST | `/api/agent/runs` | Python Agent 실행 |
| POST | `/api/agent/runs/{run_id}/approve` | 직접 구현한 승인 처리 |
| POST | `/api/agent/runs/{run_id}/reject` | 직접 구현한 거절 처리 |
| POST | `/api/evaluations/run` | 동일 Tool 시나리오의 Provider 평가 |

Tool 선택과 Agent 실행 요청에는 선택적으로 `provider`를 전달합니다.

```json
{
  "provider": "gemini",
  "message": "부산 숙소를 찾아줘"
}
```

Tool 실행 API는 Provider와 독립적이며 allowlist를 통과한 요청만 MCP Tool
Server로 전달합니다. 입력 검증과 PostgreSQL 조회는 MCP Server가 담당합니다.
