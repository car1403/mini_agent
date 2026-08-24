# Routing Agent와 Handler Allowlist

## 자동 라우팅

`lab_id=auto` 요청은 Ollama Structured Output으로 다음 계약을 생성합니다.

```json
{
  "lab_id": "parking",
  "confidence": 0.96,
  "reason": "차량 번호와 주차장 문 열기 요청입니다."
}
```

Routing Agent는 Lab을 **제안만** 합니다. Routing Service는 `unknown`과 낮은 confidence를
거절하고 사용자에게 Lab을 다시 묻습니다.

## Handler Allowlist

모델이 반환한 함수명이나 Python 경로를 실행하지 않습니다. 코드에 등록된 Handler만
선택합니다.

```python
WORKFLOW_HANDLERS = {
    "parking": parking_service.run,
    "air_conditioner": air_conditioner_service.run,
    "parcel_locker": parcel_locker_service.run,
    "inventory": inventory_service.run,
}
```

카페·도서관·여행도 명시적으로 import한 Agent 함수만 호출합니다.

## 두 단계 Agent 호출

자동 Workflow 요청에서는 서로 다른 책임으로 Ollama를 두 번 사용할 수 있습니다.

```text
Routing Agent: 어느 Lab인가?
Domain Agent: 해당 Lab에 필요한 arguments는 무엇인가?
```

명시적 Lab 선택은 첫 호출을 생략합니다. 확인 단계에서는 두 호출을 모두 생략하고
검증 당시 저장된 pending action을 사용합니다.

## 신뢰 경계

```text
Ollama 출력
→ Pydantic Schema
→ Handler Allowlist
→ Backend 정책
→ 사용자 확인
→ Tool
```

LLM 출력은 항상 제안이며, 어느 단계에서도 실행 권한으로 취급하지 않습니다.

