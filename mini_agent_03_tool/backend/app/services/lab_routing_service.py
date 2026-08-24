"""검증된 요청을 허용된 Workflow 또는 Agent Handler로 전달합니다.

두 실행 형태를 의도적으로 구분합니다.

- Agent-assisted Workflow: 주차장·에어컨·택배함·재고. Service가 순서와 정책을
  소유하고 도메인 Agent는 자연어 arguments 추출 단계에만 참여합니다.
- Agent-controlled Loop: 카페·도서관·여행. Agent가 현재 상태에 따라 재질문,
  다음 조회 Tool 또는 종료를 선택합니다.

어떤 경우에도 Ollama가 반환한 함수명이나 Python 경로를 동적으로 실행하지 않고,
아래 Allowlist에 등록된 Handler만 호출합니다.
"""
from app.agents.cafe_order_agent import run_cafe_order_agent
from app.agents.lab_routing_agent import classify_lab, explicit_decision
from app.agents.travel_planning_agent import run_travel_planning_agent
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRunRequest, LabRunResponse
from app.services import air_conditioner_service, inventory_service, library_service, parcel_locker_service, parking_service

AGENT_LABS = {"cafe", "library", "travel"}
WORKFLOW_HANDLERS = {
    "parking": parking_service.run,
    "air_conditioner": air_conditioner_service.run,
    "parcel_locker": parcel_locker_service.run,
    "inventory": inventory_service.run,
}

def route_and_run(payload: LabRunRequest) -> LabRunResponse:
    """라우팅 제안 검증부터 Handler 결과의 공통 응답 변환까지 조정합니다."""
    # 확인 단계에서는 최초 검증 때 저장한 Lab과 arguments를 사용합니다. 자연어를
    # 다시 분석하면 같은 요청이 다른 Lab이나 값으로 바뀔 수 있기 때문입니다.
    pending = lab_repository.get_pending_action(payload.action_id or "") if payload.confirmed else None
    if pending is not None:
        routing = explicit_decision(pending["lab_id"])
        routing.reason = "확인 전 저장된 pending action의 Lab을 사용했습니다."
    else:
        # 자동 모드에서만 LLM Agent가 Lab을 분류합니다. 명시 모드는 반복 가능한
        # 수업과 테스트를 위해 결정적인 선택으로 처리합니다.
        routing = classify_lab(payload.message) if payload.lab_id == "auto" else explicit_decision(payload.lab_id)
    lab_id = routing.lab_id
    if lab_id == "unknown" or routing.confidence < 0.55:
        return LabRunResponse(lab_id="unknown", execution_type="workflow", status="needs_clarification", final_answer="주차장, 에어컨, 택배함, 카페, 도서관, 재고, 여행 중 어떤 Lab인지 알려주세요.", termination_reason="route_uncertain", routing=routing)
    if lab_id in WORKFLOW_HANDLERS:
        # Workflow Handler가 Agent 추출 → 검증 → 정책 → 확인 → Tool 순서를 소유합니다.
        outcome = WORKFLOW_HANDLERS[lab_id](payload)
    elif lab_id == "cafe": outcome = run_cafe_order_agent(payload.session_id, payload.message, payload.arguments)
    elif lab_id == "library": outcome = library_service.run(payload)
    elif lab_id == "travel": outcome = run_travel_planning_agent(payload.session_id, payload.message, payload.arguments)
    # 서로 다른 Handler의 내부 표현을 Frontend가 공통으로 관찰할 수 있는 계약으로 바꿉니다.
    return LabRunResponse(lab_id=lab_id, execution_type="agent" if lab_id in AGENT_LABS else "workflow", status=outcome["status"], final_answer=outcome["answer"], state=outcome["state"], tool_calls=outcome["calls"], trace=outcome["trace"], termination_reason=outcome["reason"], routing=routing)
