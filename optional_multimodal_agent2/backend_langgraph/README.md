# 10 LangGraph Agent Backend

10번과 동일한 API 계약과 여행 기능을 실제 LangGraph로 구현한 FastAPI
Backend입니다. `StateGraph`, Node, Conditional Edge, Checkpointer,
`interrupt()`와 `Command(resume=...)`를 학습합니다.

## 실행

LangGraph Agent는 기본적으로 `http://127.0.0.1:8001`에서 실행합니다. 프로젝트
루트 `.env`의 `LANGGRAPH_AGENT_API_URL`도 같은 주소를 사용해야 합니다.
Tool 선택과 실행에는 별도로 실행한 Travel Tools MCP Server
(`http://127.0.0.1:8020/mcp`)가 필요합니다.

```powershell
cd C:\mini_agent\optional_multimodal_agent\backend_langgraph
..\.venv\Scripts\python.exe -m app.main
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

Agent 요청의 `provider`는 Graph State에 저장됩니다. 일정 생성 Node는 선택한
GPT·Gemini·Ollama를 사용하고 승인 재개 시에도 Checkpoint에 저장된 최초
Provider를 유지합니다.

## 승인 재개

1. 최초 실행은 `approval` Node에서 중단됩니다.
2. PostgreSQL `PostgresSaver`가 같은 `thread_id`의 상태를 보존합니다.
3. 승인·거절 API가 `Command(resume=...)`로 Graph를 재개합니다.

Checkpoint는 PostgreSQL에 영속화되므로 Backend를 재시작해도 승인 대기 상태를
같은 `thread_id`로 다시 이어갈 수 있습니다.

공통 API 경로와 요청·응답 구조는 같은 프로젝트의 `backend_python`과 동일합니다.
