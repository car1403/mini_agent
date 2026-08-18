# Starter

다음 순서로 하나씩 작성합니다.

1. `TravelState`에 `message`, `destination`, `status`, `trace`를 정의합니다.
2. `extract` Node에서 `destination` 변경값만 반환합니다.
3. 목적지가 없으면 `ask_user`, 있으면 `create_plan`을 반환하는 Routing 함수를 작성합니다.
4. `START → extract`와 두 종료 경로를 연결합니다.
5. Reducer를 사용해 각 Node 이름을 `trace`에 누적합니다.
6. 두 입력을 실행해 `trace`를 비교합니다.

처음부터 완성 Graph를 복사하지 말고 `steps/01~06`을 따라 작성합니다.
