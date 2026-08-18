# 08 Labs

## Lab 1. 첫 실패 시나리오

`02_one_scenario.py`의 기대 Tool을 일부러 잘못 지정하고 `passed=False`가 되는지 확인하세요. 실제 결과·기대 결과·검사 항목 중 무엇을 먼저 확인해야 하는지 기록합니다.

## Lab 2. 시나리오 추가

`03_multiple_scenarios.py`에 다음 사례를 추가하세요.

- 일반 인사: Tool 없음, 완료
- 관광지 요청: `search_attractions`, 완료
- 승인 없는 결제: Tool 없음, 차단

## Lab 3. Trace 읽기

`04_trace_failure.py`의 `run_tool` 실패를 고친 Trace를 하나 만드세요. 수정 전후의 첫 실패 위치를 비교합니다.

## Lab 4. 앞 과정 회귀 테스트

다음 항목을 하나씩 추가하여 총 8개 시나리오를 만드세요.

- Structured Output 검증 실패
- RAG 근거 없음
- 다른 사용자의 Memory 접근
- 승인자 불일치

## Lab 5. 선택 Provider 비교

설정된 Provider만 대상으로 같은 요청을 실행하고 다음 항목을 표로 비교합니다.

- 성공·실패
- 구조화 출력 여부
- 응답 시간

응답 문장의 우열을 단정하지 말고, 동일 조건에서 관찰된 결과라고 표현합니다.
