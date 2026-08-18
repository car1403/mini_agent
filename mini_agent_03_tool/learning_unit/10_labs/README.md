# 03 Tool Use 실습

## 실습 1. Schema 오류 관찰

`02_tool_schema_validation.py`에 다음 입력을 추가하고 오류의 `field`, `message`, `type`을 기록합니다.

- `city`가 빈 문자열
- `guests`가 0명
- `guests`가 11명
- `check_out`이 `check_in`과 같은 날짜
- 정의되지 않은 `payment` 인자

## 실습 2. 관광지 Tool 선택

`03_mock_tool_selection.py`에 다음 문장을 추가합니다.

- 제주 관광지를 추천해줘
- 부산에서 가볼 만한 곳을 알려줘
- 여행을 준비하고 있어요

앞의 두 문장만 `search_attractions`를 선택하고 마지막 문장은 Tool을 선택하지 않아야 합니다.

## 실습 3. 안전한 관광지 Tool 실행

`04_safe_tool_execution.py`에 `search_attractions(city, category)`를 추가합니다.

- `category`: `nature`, `culture`, `food`, `all`
- Allowlist 등록 전과 후의 결과 비교
- 잘못된 category가 `TOOL_VALIDATION_ERROR`인지 확인

## 실습 4. 오류 코드 통일

다음 실패를 공통 오류 Schema로 반환합니다.

- 미등록 Tool: `TOOL_NOT_ALLOWED`
- arguments 오류: `TOOL_VALIDATION_ERROR`
- 함수 내부 오류: `TOOL_EXECUTION_ERROR`

## 실습 5. Agent Loop 추적

`05_tool_result_to_answer.py`에서 각 단계를 별도로 출력합니다.

1. 사용자 질문
2. Tool Call
3. Tool Result
4. 최종 답변

Tool Result의 기온을 26도에서 30도로 바꿨을 때 최종 답변도 함께 바뀌는지 확인합니다.

## 실습 6. Provider 비교

준비된 Provider만 선택해 같은 질문을 보냅니다. 다음 항목을 표로 기록합니다.

- 선택한 Tool
- arguments
- 응답 시간
- 성공 또는 실패
- 실패한 경우 오류 메시지

Provider 하나가 실패해도 전체 비교가 중단되지 않아야 합니다.
