# Mini Agent 06 초보자 진행 순서

## 1. 코드 실행

1. `01_state.py`: 공유 데이터
2. `02_node.py`: 변경값 반환
3. `03_edge.py`: 고정 순서
4. `04_conditional_edge.py`: 경로 선택
5. `05_small_travel_graph.py`: 첫 Graph와 Mermaid 구조
6. `06_reducer.py`: 값 교체와 목록 누적
7. `07_loop_and_stop.py`: 반복과 실패 종료
8. `08_checkpoint_and_thread.py`: Thread별 State
9. `09_python_vs_langgraph.py`: 같은 분기 흐름 비교

## 2. 화면에서 관찰

1. 실행 전에 예상 경로를 말합니다.
2. 입력값을 바꿉니다.
3. 실제 `trace`를 확인합니다.
4. 예상 경로와 실제 경로를 비교합니다.
5. 마지막에만 완성 Agent 화면을 확인합니다.

## 완료 체크

- [ ] State, Node, Edge를 한 문장으로 설명할 수 있습니다.
- [ ] Node와 Routing 함수의 역할을 구분합니다.
- [ ] Reducer가 필요한 State와 필요하지 않은 State를 구분합니다.
- [ ] 목적지 유무에 따른 경로를 예상할 수 있습니다.
- [ ] 반복 Graph에 종료 조건이 필요한 이유를 설명합니다.
- [ ] 같은 `thread_id`와 다른 `thread_id`의 차이를 설명합니다.
- [ ] Python Workflow와 LangGraph 결과가 같을 수 있음을 이해합니다.
