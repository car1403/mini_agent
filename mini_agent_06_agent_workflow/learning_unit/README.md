# 06 LangGraph Workflow

## 이번 단계의 목표

일반 Python으로 만든 실행 흐름을 State, Node, Edge를 사용한 Graph로 표현할 수 있습니다.

복잡한 Agent를 바로 만들지 않습니다. 먼저 작은 함수와 Mock 데이터로 Graph 구성 요소를 하나씩 확인합니다.

```text
일반 Python 함수
→ State
→ Node
→ Edge
→ 조건 분기
→ Reducer
→ 반복과 종료
→ Checkpoint와 thread_id
```

## 다섯 가지 핵심 용어

| 용어 | 초보자 설명 |
| --- | --- |
| State | Workflow 함수들이 함께 사용하는 데이터 |
| Node | State를 받고 변경할 값을 반환하는 함수 |
| Edge | 다음에 실행할 Node를 연결하는 선 |
| Conditional Edge | State를 보고 다음 경로를 선택하는 분기 |
| Reducer | 여러 Node의 변경값을 교체할지 누적할지 정하는 규칙 |

Node는 State 전체를 새로 만들거나 직접 변경하기보다 변경할 값만 `dict`로 반환합니다. Routing 함수는 값을 만들지 않고 다음 Node 이름만 선택합니다. 목록처럼 계속 쌓을 값에는 Reducer를 지정합니다.

## 예제 순서

| 순서 | 예제 | LangGraph 필요 | 새로운 개념 |
| --- | --- | --- | --- |
| 01 | `01_state.py` | 아니요 | State |
| 02 | `02_node.py` | 아니요 | Node와 부분 변경값 |
| 03 | `03_edge.py` | 아니요 | 고정 실행 순서 |
| 04 | `04_conditional_edge.py` | 아니요 | 조건 분기 |
| 05 | `05_small_travel_graph.py` | 예 | 첫 `StateGraph`·Mermaid 구조 |
| 06 | `06_reducer.py` | 예 | 값 교체와 목록 누적 |
| 07 | `07_loop_and_stop.py` | 예 | 반복·최대 횟수·실패 종료 |
| 08 | `08_checkpoint_and_thread.py` | 예 | Checkpoint·`thread_id` |
| 09 | `09_python_vs_langgraph.py` | 예 | 같은 분기 흐름 비교 |

처음 네 예제는 LangGraph를 사용하지 않습니다. 같은 개념을 일반 Python으로 이해한 다음 05에서 실제 Graph로 옮깁니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_06_langgraph\learning_unit
python .\01_state.py
python .\02_node.py
python .\03_edge.py
python .\04_conditional_edge.py
python .\05_small_travel_graph.py
python .\06_reducer.py
python .\07_loop_and_stop.py
python .\08_checkpoint_and_thread.py
python .\09_python_vs_langgraph.py
```

`05_small_travel_graph.py`는 실행할 때 Graph의 Mermaid 텍스트도 출력합니다. Node와 Edge 코드를 읽은 뒤 출력된 구조를 함께 비교합니다.

## Reducer를 쓰는 이유

일반적인 State 필드는 새 값으로 교체됩니다. `trace`, 메시지 목록처럼 이전 값 뒤에 계속 추가해야 하는 필드는 Reducer를 사용합니다.

```python
from operator import add
from typing import Annotated

trace: Annotated[list[str], add]
```

이렇게 선언하면 각 Node는 전체 목록을 다시 만들지 않고 `{"trace": ["node_name"]}`처럼 새 항목만 반환할 수 있습니다.

## 분기와 반복을 읽는 방법

```text
START
  → extract
     ├─ 목적지 없음 → ask_user → END
     └─ 목적지 있음 → create_plan → END
```

```text
START → create_plan
          ├─ 예산 통과 → finish → END
          ├─ 수정 가능 → revise → create_plan
          └─ 반복 초과 → fail → END
```

반복 Graph에는 반드시 최대 반복 횟수와 실패 종료 경로가 있어야 합니다.

## Checkpoint 범위

`InMemorySaver`는 같은 프로세스에서 Checkpoint와 `thread_id`를 이해하기 위한 교육용 저장소입니다. 서버를 재시작하면 사라집니다. 운영 환경에서 재시작 후 재개가 필요하면 영구 Checkpointer를 사용해야 합니다.

Checkpointer는 각 단계의 State를 Thread별로 저장합니다. 같은 `thread_id`는 이전 State를 이어가고 다른 `thread_id`는 별도 실행으로 관리됩니다. [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)

## 이번 단계에서 제외하는 내용

- 실제 LLM·Tool·RAG·Memory를 한 Graph에 통합
- `interrupt()` 승인과 재개
- 병렬 Node, Subgraph, 운영용 Checkpointer

승인·중단·재개는 다음 `07_human-approval-and-safety`에서 학습합니다. Mini06의 완성 Backend는 마지막 선택 시연용입니다.

## 공식 참고 자료

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
