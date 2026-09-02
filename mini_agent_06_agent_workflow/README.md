# Mini Agent 06 · 초보자 LangGraph

일반 Python Workflow를 State, Node, Edge를 사용하는 LangGraph로 한 단계씩 옮깁니다.

이번 단계의 목표는 복잡한 Agent 완성이 아닙니다.

> 같은 실행 흐름을 일반 Python과 LangGraph로 표현하고, State와 실행 경로를 확인할 수 있다.

## 학습 순서

```text
State → Node → Edge → 조건 분기 → 작은 Graph
      → Reducer → 반복과 종료 → Checkpoint → Python과 비교
```

`learning_unit`과 `steps`는 같은 9개 파일을 사용합니다. 01~04는 일반 Python, 05~09는 실제 LangGraph 예제입니다.

## Streamlit 초보자 메뉴

1. Graph 구성 요소와 Reducer
2. 조건 분기
3. 반복과 종료
4. Checkpoint와 `thread_id`
5. 일반 Python과 LangGraph 비교

기존 LLM·Tool·RAG·Memory·완성 Agent 화면은 선택 시연으로 분리했습니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_06_langgraph
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

학습용 LangGraph Backend:

```powershell
cd backend_langgraph
uvicorn app.main:app --reload --port 8001
```

새 터미널에서 Streamlit을 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_06_langgraph
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

Python Backend 8000은 마지막 완성본 비교에서만 선택적으로 실행합니다.

## Checkpoint 주의

학습용 API는 `InMemorySaver`를 사용합니다. 같은 Backend 프로세스에서는 `thread_id`별 State가 유지되지만 Backend를 재시작하면 사라집니다. 운영용 영구 Checkpointer와 승인 재개는 다음 단계에서 다룹니다.

## 이번 단계에서 하지 않는 것

- 실제 LLM 응답을 Graph 분기 기준으로 사용
- 실제 예약이나 결제 Tool 실행
- `interrupt()` 승인과 재개
- 병렬 Node와 Subgraph

완성 Backend에는 다음 단계 미리보기 코드가 있지만 초보자 학습 메뉴에서는 실행하지 않습니다.
