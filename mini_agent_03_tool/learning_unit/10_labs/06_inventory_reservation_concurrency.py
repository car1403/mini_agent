"""Lab 06 — 예약 직전 재검증과 낙관적 잠금으로 동시 변경을 감지합니다.

학습 분류:
- 현재 성격: 동시성·낙관적 잠금
- Agent 여부: 아니오
- 권장 방향: 안전한 Tool 실행 정책으로 유지
- 판단 근거: 재고와 Version은 실행 직전 Backend가 원자적으로 검사해야 합니다.
  Agent가 이전 Tool Result만 믿고 예약 성공을 결정해서는 안 됩니다.

Backend 디렉터리 기준 역할:
- `schemas/`: ReserveInventoryInput이 SKU·수량·예상 Version 입력 계약을 정의합니다.
- `tools/`: get_inventory와 reserve_inventory가 재고 조회·예약 실행 Tool입니다.
- `services/`: Version 비교와 수량 확인이 동시성·재고 업무 정책을 담당합니다.
- `agents/`: 별도 Agent 없이 호출자가 조회 결과의 Version을 예약 요청에 전달합니다.
- `routers/`: 이 파일에서는 `__main__` 실행부가 두 요청의 경쟁 상황을 재현합니다.
- `providers/`: 예약의 최종 권한은 서버에 있으므로 LLM Provider를 사용하지 않습니다.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# [schemas/] 예약 수량과 조회 당시 Version을 요구하는 Tool 입력 계약입니다.
class ReserveInventoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(min_length=1)
    quantity: int = Field(ge=1)
    expected_version: int = Field(ge=1)


# [학습용 저장소] 실제 Backend에서는 Version 열이 있는 재고 DB/Repository가 담당합니다.
INVENTORY = {"SKU-001": {"available": 5, "version": 1}}


# [tools/] SKU의 현재 재고 수량과 Version을 조회하는 읽기 전용 Tool입니다.
def get_inventory(sku: str) -> dict[str, Any]:
    item = INVENTORY.get(sku)
    return {"sku": sku, **item} if item else {"sku": sku, "not_found": True}


# [tools/ + services 정책] 입력을 검증하고 Version·수량 정책을 통과할 때만 예약합니다.
def reserve_inventory(arguments: dict[str, Any]) -> dict[str, Any]:
    args = ReserveInventoryInput.model_validate(arguments)
    item = INVENTORY.get(args.sku)
    if item is None:
        return {"reserved": False, "code": "NOT_FOUND"}

    # DB에서는 UPDATE ... WHERE version = expected_version와 같은 원자적 조건 갱신을 사용합니다.
    if item["version"] != args.expected_version:
        return {"reserved": False, "code": "VERSION_CONFLICT", "current": get_inventory(args.sku)}
    if item["available"] < args.quantity:
        return {"reserved": False, "code": "INSUFFICIENT_STOCK", "current": get_inventory(args.sku)}

    item["available"] -= args.quantity
    item["version"] += 1
    return {"reserved": True, "sku": args.sku, "quantity": args.quantity, "remaining": item["available"], "version": item["version"]}


# [routers/ 대체] 두 요청이 같은 Version을 읽은 경쟁 상황과 재시도를 재현합니다.
if __name__ == "__main__":
    first_read = get_inventory("SKU-001")
    second_read = get_inventory("SKU-001")
    print("요청 A 조회:", first_read)
    print("요청 B 조회:", second_read)

    result_a = reserve_inventory({"sku": "SKU-001", "quantity": 4, "expected_version": first_read["version"]})
    result_b = reserve_inventory({"sku": "SKU-001", "quantity": 3, "expected_version": second_read["version"]})
    print("요청 A 예약:", result_a)
    print("요청 B 예약:", result_b)

    refreshed = get_inventory("SKU-001")
    retry_b = reserve_inventory({"sku": "SKU-001", "quantity": 3, "expected_version": refreshed["version"]})
    print("요청 B 재조회 후 재시도:", retry_b)
