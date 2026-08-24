# 일곱 가지 Tool Use 시나리오

## 1. 주차장 출입

```text
Parking Agent → 차량 조회 Tool → 출입 정책 → 확인 → 문 열기 Tool
```

등록·활성 차량만 pending action을 발급합니다.

## 2. 에어컨 제어

```text
Air Conditioner Agent → 히스테리시스 규칙 → 확인 → 제어 Tool
```

27°C 이상에서 켜고 23°C 이하에서 끄며 중간 구간은 상태를 유지합니다.

## 3. 택배함

```text
Parcel Locker Agent → 코드·만료·재사용 검사 → 확인 → 문 열기 Tool
```

Pending action과 일회성 코드로 중복 실행을 차단합니다.

## 4. 카페 주문

```text
Cafe Agent → 주문값 병합 → 누락 시 재질문 → Mock 주문 Tool
```

Session에 메뉴·크기·수량을 유지합니다.

## 5. 도서 대출

```text
Library Agent → 회원·도서·대출 목록 Tool → Backend 대출 정책
```

Agent는 근거만 수집하고 대출 가능 여부는 Backend가 결정합니다.

## 6. 재고 예약

```text
Inventory Agent → 재고 조회 → Version·수량 검사 → 확인 → 조건부 예약 Tool
```

확인 대기 중 Version이 달라져도 실행 직전에 다시 감지합니다.

## 7. 여행 준비

```text
Travel Agent → 도시·날짜 재질문 → 현재 날씨 또는 예보 → 관광지 → 종료
```

읽기 전용 Multi-Tool Agent로 승인 단계가 필요하지 않습니다.

## Frontend 관찰 항목

통합 화면에서는 다음을 함께 비교합니다.

- Routing 결과와 confidence
- Workflow 또는 Agent 실행 형태
- Tool 이름과 arguments
- Backend 정책과 현재 Mock 상태
- 전체 Trace와 종료 이유

