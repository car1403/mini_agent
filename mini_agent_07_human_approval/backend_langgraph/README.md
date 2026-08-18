# Mini Agent 07 · LangGraph Backend

같은 프로젝트의 Python Backend와 동일한 API 계약과 여행 기능을 실제 LangGraph로 구현한 FastAPI
Backend입니다. `StateGraph`, Node, Conditional Edge, Checkpointer,
`interrupt()`와 `Command(resume=...)`를 학습합니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_07_human_approval\backend_langgraph
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

## Graph 흐름

```text
START → extract_request
                ├─ 정보 부족 → needs_input → END
                └─ 정보 충분 → load_context → create_plan
                                              → approval(interrupt) → END
```

Graph 구현은 `app/workflows/langgraph_travel_workflow.py`에 있습니다. Agent
요청에는 `engine` 값을 보내지 않습니다. 이 Backend를 호출하는 것 자체가
LangGraph 실행을 의미합니다.

## 승인 재개

1. 최초 실행은 `approval` Node에서 중단됩니다.
2. `InMemorySaver`가 같은 `thread_id`의 상태를 보존합니다.
3. 승인·거절 API가 `Command(resume=...)`로 Graph를 재개합니다.

교육용 기본 Checkpointer는 메모리 방식이므로 Backend를 재시작하면 승인 대기
상태가 사라집니다. 영속 Checkpointer는 후속 프로젝트에서 연결합니다.

공통 API 경로와 요청·응답 구조는 같은 프로젝트의 `backend_python`과 동일합니다.
