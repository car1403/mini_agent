# 02 Labs

Lab 2~4와 Lab 8은 Backend가 필요합니다. Prompt 품질 비교에는 `gemini`, `openai`,
`ollama` 중 설정된 실제 Provider를 사용하고 `mock`은 호출 흐름만 확인합니다.

1. 상품 리뷰 업무를 `01_prompt_template_and_variables.py`에 추가합니다.
2. 고객 문의를 세 개로 늘리고 Zero-shot과 Few-shot의 일관성을 비교합니다.
3. 사용자 입력을 그대로 연결한 경우와 구분자로 감싼 경우를 비교합니다.
4. 모호한 회의 Prompt를 네 구성 요소와 출력 형식으로 개선합니다.
5. `TravelPlan`에 `estimated_budget`, `transportation`, `daily_itinerary`를 추가합니다.
6. 두 Schema의 범위·Literal·strict Boolean·추가 필드 오류를 사용자 문장으로 바꿉니다.
7. `SupportTicket`에 `sentiment`, `suggested_team`을 추가합니다.
8. `01_structured_provider_comparison.py`로 두 Schema의 Provider 결과를 비교합니다.
