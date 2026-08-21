# Agent와 Workflow 구분

## 구분 기준

Tool 사용 여부로 Agent와 Workflow를 나누지 않습니다. **다음 단계와 종료 시점을 누가
결정하는가**를 기준으로 구분합니다.

```text
Workflow: Backend 코드가 실행 순서를 소유
Agent: 현재 상태를 보고 재질문·다음 Tool·종료를 선택
```

## Agent-assisted Workflow

주차장, 에어컨, 택배함, 재고 Lab이 해당합니다.

```text
Workflow Service
→ Domain Agent가 자연어 arguments 추출
→ Pydantic 검증
→ 조회 Tool
→ Backend 정책
→ 사용자 확인
→ 상태 변경 Tool
```

Agent는 유연한 입력 해석만 담당합니다. 출입 승인, 인증 성공, 에어컨 안전 규칙,
재고 Version 비교는 결정적인 Backend 코드가 담당합니다.

## Agent-controlled Loop

카페, 도서관, 여행 Lab이 해당합니다.

- 카페 Agent는 누락된 주문값을 확인하고 재질문 또는 종료를 선택합니다.
- 도서관 Agent는 회원·도서·대출 목록 Tool을 선택해 근거를 수집합니다.
- 여행 Agent는 오늘/미래에 따라 날씨 Tool을 고르고 관광지 Tool을 이어서 선택합니다.

Agent가 다음 행동을 선택해도 Tool Allowlist, arguments Schema와 Backend 정책은 항상
적용됩니다.

## Lab 분류

| Lab | 실행 형태 | Agent 역할 | Backend 역할 |
|---|---|---|---|
| 주차장 | Agent-assisted Workflow | 차량 번호 추출 | 권한 검사와 문 열기 |
| 에어컨 | Agent-assisted Workflow | 온도 추출 | 히스테리시스와 제어 |
| 택배함 | Agent-assisted Workflow | ID·코드 추출 | 인증·만료·재사용 검사 |
| 카페 | Agent-controlled Loop | 주문값 수집과 재질문 | Mock 주문 실행 |
| 도서관 | Agent-controlled Loop | 조회 Tool 선택 | 대출 정책과 상태 변경 |
| 재고 | Agent-assisted Workflow | SKU·수량·Version 추출 | 동시성·수량 검사 |
| 여행 | Agent-controlled Loop | 재질문·Tool·종료 선택 | 읽기 결과 제공 |
