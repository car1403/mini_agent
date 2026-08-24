"""재고 예약의 동시성 정책을 소유하는 Agent-assisted Workflow입니다.

Agent는 SKU·수량·조회 Version을 구조화합니다. 실제 재고와 Version 비교, 수량 검사,
예약 성공 여부는 Backend가 결정하며 확인 시점에도 Tool이 Version을 원자적으로
재검증합니다.
"""
from app.agents.inventory_reservation_agent import extract_inventory_request
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRunRequest
from app.tools.lab_tools import get_inventory, reserve_inventory

def run(payload: LabRunRequest) -> dict:
    """인자 추출 → 재고 조회 → 정책 검사 → 확인 → 조건부 예약을 수행합니다."""
    if payload.confirmed:
        # 예약 Tool이 expected_version을 다시 확인하므로 확인 대기 중 변경도 감지합니다.
        action = lab_repository.consume_pending_action(payload.action_id or "", "inventory")
        if action is None: return result("rejected", "유효한 확인 작업을 찾지 못했습니다.", "invalid_action")
        reserved = reserve_inventory(**action["arguments"])
        answer = "재고를 예약했습니다." if reserved["reserved"] else f"예약 실패: {reserved['code']}"
        return result("completed", answer, "completed", lab_repository.snapshot("inventory"), [{"stage": "confirmed_tool_execution", "data": reserved}], [action])
    # Agent는 입력 해석만 담당하며 현재 재고량이나 성공 여부를 만들지 않습니다.
    values, extraction = extract_inventory_request(payload.message, payload.arguments)
    missing = [name for name in ("sku", "quantity", "expected_version") if getattr(values, name) is None]
    if missing: return result("needs_clarification", f"다음 정보를 알려주세요: {', '.join(missing)}", "needs_user_input", trace=[extraction])
    # 조회 Tool 결과를 기반으로 Service가 예약 가능 정책을 결정합니다.
    current = get_inventory(values.sku)
    trace = [extraction, {"stage": "get_inventory", "data": current}]
    if current.get("not_found"): return result("rejected", "SKU를 찾을 수 없습니다.", "policy_rejected", trace=trace)
    if current["version"] != values.expected_version: return result("rejected", "조회 이후 재고가 변경되었습니다. 최신 Version으로 다시 시도하세요.", "version_conflict", current, trace)
    if current["available"] < values.quantity: return result("rejected", "예약 가능한 재고가 부족합니다.", "insufficient_stock", current, trace)
    arguments = {"sku": values.sku, "quantity": values.quantity, "expected_version": values.expected_version}
    action = lab_repository.create_pending_action("inventory", "reserve_inventory", arguments)
    return result("confirmation_required", "재고와 Version을 확인했습니다. 예약 실행을 확인해 주세요.", "confirmation_required", {"pending_action_id": action["action_id"], "expires_at": action["expires_at"].isoformat(), "inventory": current}, trace, [action])

def result(status, answer, reason, state=None, trace=None, actions=None):
    return {"status": status, "answer": answer, "state": state or {}, "trace": trace or [], "reason": reason, "calls": [{"tool": item["tool_name"], "arguments": item["arguments"]} for item in (actions or [])]}

