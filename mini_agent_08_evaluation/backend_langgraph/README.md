# Mini Agent 08 · LangGraph Backend

Python Backend와 동일한 API 계약을 `StateGraph`, Node, Conditional Edge, Checkpointer, `interrupt()`와 `Command(resume=...)`로 구현합니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_08_evaluation\backend_langgraph
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8001
```

## Graph 흐름

```text
START → extract_request
                ├─ 정보 부족 → needs_input → END
                └─ 정보 충분 → load_context → create_plan
                                              → approval(interrupt) → END
```

Graph는 `app/workflows/langgraph_travel_workflow.py`에 있습니다. 승인·거절은 같은 `thread_id`로 재개하며 실행 소유자와 승인자가 일치해야 합니다.

교육용 `InMemorySaver`는 Backend를 재시작하면 상태가 사라집니다. 운영 단계에서는 영속 Checkpointer로 교체해야 합니다.

평가 API는 Python Backend와 같은 시나리오·응답 계약을 사용하므로 두 구현을 같은 기준으로 비교할 수 있습니다.
