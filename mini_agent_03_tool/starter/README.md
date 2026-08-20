# Starter · Tool Use

1. `tool_schema.py`: arguments 입력 계약을 작성합니다.
2. `tool_selector.py`: 문장에서 필요한 Tool 이름을 선택합니다.
3. `tool_runner.py`: Allowlist와 Pydantic 검증 후 실행합니다.
4. `tool_result_to_answer.py`: Tool Result로 최종 답변을 만듭니다.

선택 함수에서는 Tool을 실행하지 않습니다. 필수 입력이 빠졌다면 값을 추측하지 말고 `missing_arguments`와 사용자용 추가 질문을 만드세요. 완성본에서는 현재 날씨와 미래 예보 선택 및 Choice 모드도 비교할 수 있습니다.
