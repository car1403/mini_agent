# 06 LangGraph Workflow 실습

## 실습 1. State 필드 추가

`01_state.py`에 `nights`, `budget`를 추가합니다. 필드가 없을 수도 있도록 `total=False`의 의미를 확인합니다.

## 실습 2. Node 부분 반환

`02_node.py`의 Node가 `destination`만 반환하는 경우와 State 전체를 반환하는 경우를 비교합니다.

## 실습 3. 조건 분기

다음 입력의 예상 경로를 먼저 적고 `04_conditional_edge.py`를 실행합니다.

- `부산 여행을 준비해줘`
- `서울 여행을 준비해줘`
- `여행을 준비해줘`

서울 추출 규칙을 추가한 뒤 경로가 바뀌는지 확인합니다.

## 실습 4. 첫 Graph Trace

`05_small_travel_graph.py`에서 `trace`를 확인하고 Node 실행 순서를 화살표로 적습니다.

## 실습 5. Graph 구조 읽기

`05_small_travel_graph.py`가 출력한 Mermaid 텍스트에서 Node와 Edge를 찾습니다. 코드의 `add_node`, `add_edge`, `add_conditional_edges`와 각각 연결해 표시합니다.

## 실습 6. Reducer와 값 누적

`06_reducer.py`에서 `Annotated[list[str], add]`를 제거한 경우를 예상한 뒤 실행 결과와 비교합니다. 각 Node가 전체 `trace`가 아닌 새 항목만 반환하는 이유를 설명합니다.

## 실습 7. 반복과 종료

`07_loop_and_stop.py`의 예산을 600000, 400000, 200000으로 바꾸고 다음을 기록합니다.

- 최종 `status`
- `iteration`
- `estimated_budget`
- `trace`

`max_iterations`를 0과 2로 바꿔 무한 반복 없이 종료되는지 확인합니다.

## 실습 8. Thread 격리

`travel-a`, `travel-b`를 각각 두 번 실행합니다. 두 Thread의 `visits`가 섞이지 않는지 확인합니다.

## 실습 9. Checkpoint History

`graph.get_state_history(config)`에서 각 Checkpoint의 `values`, `next`, `metadata.step`을 출력합니다.

## 실습 10. Python과 LangGraph 비교

같은 입력에 대해 결과, 분기 위치, State 확인 방법, 테스트 방법을 표로 비교합니다.

## 실습 11. 흔한 오류 고치기

복사본에서 다음 오류를 하나씩 만든 뒤 원인을 찾아 복구합니다.

- State 필드 이름을 잘못 작성합니다.
- Routing 함수가 등록하지 않은 Node 이름을 반환하게 합니다.
- 반복 Graph의 `max_iterations` 검사를 제거합니다.

마지막 오류는 실행하지 말고 코드만 보고 무한 반복 가능성을 설명합니다.
