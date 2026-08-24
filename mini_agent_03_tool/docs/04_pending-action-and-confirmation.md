# Pending Action과 사용자 확인

## 필요한 이유

주차장 문 열기, 에어컨 제어, 택배함 열기, 도서 대출, 재고 예약은 Mock이어도 상태를
변경합니다. 교육 예제에서도 조회와 상태 변경을 분리하고 사용자 확인을 요구합니다.

## 올바른 순서

```text
Agent arguments 추출
→ Pydantic 검증
→ 조회 Tool
→ Backend 정책 통과
→ pending_action 발급
→ 사용자 확인
→ 저장된 arguments로 상태 변경 Tool 실행
```

등록되지 않은 차량이나 만료된 인증 코드처럼 실행할 수 없는 요청에는 확인을 요구하지
않습니다.

## Pending Action 내용

```json
{
  "action_id": "UUID",
  "lab_id": "parking",
  "tool_name": "open_gate",
  "arguments": {"plate_number": "12가3456"},
  "expires_at": "..."
}
```

- 기본 유효 시간은 120초입니다.
- 한 번 소비하면 Repository에서 제거됩니다.
- 확인 시 자연어를 다시 분석하지 않습니다.
- action에 저장된 Lab으로 다시 라우팅합니다.
- 현재 구현은 In-memory Mock이므로 서버 재시작 시 사라집니다.

## 실제 서비스 확장

운영 환경에서는 Redis TTL 또는 DB Transaction으로 교체하고 사용자 ID, 권한,
감사 로그, Idempotency Key를 함께 검증해야 합니다. Mock Repository는 이러한 계약을
학습하기 위한 최소 구현입니다.

