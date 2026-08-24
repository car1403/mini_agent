"""7개 Tool Use Lab의 단일 HTTP 진입점입니다.

Router는 요청 Schema 검증과 HTTP 오류 변환만 담당합니다. 어느 Lab을 실행할지,
Workflow와 Agent 중 무엇을 사용할지, 상태 변경을 허용할지는 Routing Service와
각 도메인 Service가 결정합니다. 이 경계를 유지해야 HTTP 계층에 업무 규칙이
섞이지 않고 같은 실행 로직을 테스트나 다른 UI에서도 재사용할 수 있습니다.
"""
from fastapi import APIRouter, HTTPException
from app.repositories.lab_repository import lab_repository
from app.schemas.lab import LabRunRequest, LabRunResponse
from app.services.lab_routing_service import route_and_run

lab_router = APIRouter(prefix="/api/labs", tags=["03 · Tool Use Labs"])

@lab_router.post("/run", response_model=LabRunResponse)
def run_lab(payload: LabRunRequest) -> LabRunResponse:
    """단일 요청 계약을 Routing Service에 전달합니다.

    `lab_id=auto`이면 Ollama Routing Agent가 Lab을 제안하고, 명시된 Lab이면
    결정적으로 해당 Handler를 사용합니다. Router는 Agent 결과를 직접 신뢰하거나
    Tool을 직접 실행하지 않습니다.
    """
    try: return route_and_run(payload)
    except Exception as error: raise HTTPException(status_code=502, detail=f"Lab 실행에 실패했습니다: {error}") from error

@lab_router.post("/reset")
def reset_labs() -> dict:
    """교육용 Mock 상태만 초기화합니다. 실제 외부 장치나 DB에는 접근하지 않습니다."""
    lab_repository.reset(); return {"reset": True, "note": "모든 In-memory Mock 상태를 초기화했습니다."}

