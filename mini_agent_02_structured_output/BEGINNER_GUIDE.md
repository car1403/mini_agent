# 02 초보자 가이드 · Prompt와 Structured Output

## 오늘의 목표

자유로운 LLM 문장을 곧바로 서비스에 사용하지 않고, 미리 정한 `TravelPlan`
계약으로 검증하는 이유와 방법을 이해합니다.

## 추천 순서

```text
00 Prompt 네 부분
→ 01 일반 dict와 Pydantic
→ 02 여행 JSON 정상·오류 검증
→ Starter TODO
→ Prompt 구성 메뉴
→ Pydantic 검증 메뉴
→ Mock Structured Output
→ 실제 Provider 비교
```

## 학생이 꼭 구분할 것

- JSON 문법이 맞아도 필수 필드나 값의 범위가 틀릴 수 있습니다.
- Pydantic 검증은 LLM을 호출하지 않는 Python 기능입니다.
- Structured Output은 LLM에게 Schema를 제공하지만 Backend에서 다시 검증합니다.
- 오류는 숨기지 않고 어떤 Provider와 필드에서 발생했는지 보여줍니다.

## 이전 Frontend 수업과 같은 부분

```text
app_pages → clients/agent_client.py → core/api_client.py
Backend main.py → routers/agent_router.py → services/schemas
```

화면과 API 연결 방식은 새로 배우지 않습니다. 이번 단계에서 새로 배우는 코드는
Prompt 조립, `TravelPlan` 검증, Provider Structured Output뿐입니다.

## 완료 체크

- [ ] Prompt의 네 구성 요소를 설명할 수 있다.
- [ ] JSON 오류와 Pydantic 오류를 구분할 수 있다.
- [ ] `extra="forbid"`가 필요한 이유를 설명할 수 있다.
- [ ] Mock 결과를 `TravelPlan`으로 검증할 수 있다.
- [ ] 동일 Schema의 Gemini·GPT·Llama 결과를 비교할 수 있다.
