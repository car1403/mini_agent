from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.providers.factory import (
    provider_status,
    run_with_optional_fallback,
)
from app.rag.policies import search as search_policies
from app.repositories.store import store
from app.schemas.models import (
    AgentDecisionRequest,
    AgentRunRequest,
    ApiResponse,
    EvaluationRunRequest,
    KnowledgeSearchRequest,
    MemoryCreateRequest,
    ProviderGenerateRequest,
    ToolRunRequest,
    ToolSelectRequest,
    TravelExtractRequest,
    TravelPlan,
)
from app.services.evaluation_service import run_evaluation
from app.services.travel_service import (
    add_memory,
    extract_travel_request,
    new_trace_id,
)
from app.tools.travel_tools import run_tool, select_tool
from app.workflows.langgraph_travel_workflow import (
    resume_langgraph_run,
    start_langgraph_run,
)


router = APIRouter()


def ok(data: object, trace_id: str | None = None) -> ApiResponse:
    return ApiResponse(success=True, data=data, trace_id=trace_id or new_trace_id())


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "agent_type": "langgraph",
        "mode": settings.app_mode,
        "llm_provider": settings.llm_provider,
        "storage_mode": settings.storage_mode,
    }


@router.get("/api/providers/status", response_model=ApiResponse)
def providers() -> ApiResponse:
    return ok(
        {
            "active": settings.llm_provider,
            "fallback_enabled": settings.llm_fallback_enabled,
            "providers": provider_status(),
        }
    )


@router.post("/api/providers/generate", response_model=ApiResponse)
def generate(payload: ProviderGenerateRequest) -> ApiResponse:
    try:
        result = run_with_optional_fallback(
            lambda provider: provider.generate(payload.system_prompt, payload.message),
            payload.provider,
        )
        return ok(result.to_dict())
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"LLM 호출 실패: {error}") from error


@router.post("/api/providers/travel-plan", response_model=ApiResponse)
def generate_travel_plan(payload: ProviderGenerateRequest) -> ApiResponse:
    try:
        result = run_with_optional_fallback(
            lambda provider: provider.generate_structured(
                payload.system_prompt,
                payload.message,
                TravelPlan,
            ),
            payload.provider,
        )
        return ok(result.to_dict())
    except (ValueError, RuntimeError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"LLM 호출 실패: {error}") from error


@router.post("/api/travel/extract", response_model=ApiResponse)
def extract(payload: TravelExtractRequest) -> ApiResponse:
    return ok(extract_travel_request(payload.message, payload.reference_date))


@router.post("/api/tools/select", response_model=ApiResponse)
def choose_tool(payload: ToolSelectRequest) -> ApiResponse:
    return ok(select_tool(payload.message))


@router.post("/api/tools/run", response_model=ApiResponse)
def execute_tool(payload: ToolRunRequest) -> ApiResponse:
    try:
        return ok(run_tool(payload.tool_name, payload.arguments))
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/api/knowledge/search", response_model=ApiResponse)
def knowledge(payload: KnowledgeSearchRequest) -> ApiResponse:
    results = search_policies(payload.query, payload.limit)
    return ok({"grounded": bool(results), "documents": results})


@router.post("/api/evaluations/run", response_model=ApiResponse)
def evaluate_agent(payload: EvaluationRunRequest) -> ApiResponse:
    scenarios = [item.model_dump() for item in payload.scenarios]
    return ok(run_evaluation(scenarios or None))


@router.get("/api/users/{user_id}/memories", response_model=ApiResponse)
def list_memories(user_id: str) -> ApiResponse:
    return ok(store.list_memories(user_id))


@router.post("/api/users/{user_id}/memories", response_model=ApiResponse)
def create_memory(user_id: str, payload: MemoryCreateRequest) -> ApiResponse:
    try:
        return ok(add_memory(user_id, payload.key, payload.value))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.delete("/api/users/{user_id}/memories/{memory_id}", response_model=ApiResponse)
def delete_memory(user_id: str, memory_id: str) -> ApiResponse:
    if not store.delete_memory(user_id, memory_id):
        raise HTTPException(status_code=404, detail="Memory를 찾을 수 없습니다.")
    return ok({"deleted": True})


@router.post("/api/agent/runs", response_model=ApiResponse)
def create_run(payload: AgentRunRequest) -> ApiResponse:
    return ok(start_langgraph_run(payload.model_dump()))


@router.get("/api/agent/runs/{run_id}", response_model=ApiResponse)
def get_run(run_id: str) -> ApiResponse:
    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="실행을 찾을 수 없습니다.")
    return ok(run)


@router.post("/api/agent/runs/{run_id}/approve", response_model=ApiResponse)
def approve_run(run_id: str, payload: AgentDecisionRequest) -> ApiResponse:
    try:
        result = resume_langgraph_run(
            run_id, "approve", payload.actor, payload.note
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if result is None:
        raise HTTPException(status_code=404, detail="실행을 찾을 수 없습니다.")
    return ok(result)


@router.post("/api/agent/runs/{run_id}/reject", response_model=ApiResponse)
def reject_run(run_id: str, payload: AgentDecisionRequest) -> ApiResponse:
    try:
        result = resume_langgraph_run(
            run_id, "reject", payload.actor, payload.note
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    if result is None:
        raise HTTPException(status_code=404, detail="실행을 찾을 수 없습니다.")
    return ok(result)
