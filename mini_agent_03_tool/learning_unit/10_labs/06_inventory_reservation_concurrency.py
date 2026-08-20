"""재고 예약 직전에 재검증하고 낙관적 잠금으로 동시 변경을 감지합니다."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ReserveInventoryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(min_length=1)
    quantity: int = Field(ge=1)
    expected_version: int = Field(ge=1)


INVENTORY = {"SKU-001": {"available": 5, "version": 1}}


def get_inventory(sku: str) -> dict[str, Any]:
    item = INVENTORY.get(sku)
    return {"sku": sku, **item} if item else {"sku": sku, "not_found": True}


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
