"""Mini Agent 02의 Prompt·Pydantic·Structured Output API를 제공합니다.

`app.main`이 등록하며 Swagger의 `02 · Prompt와 구조화 출력` 그룹에 표시됩니다.
"""

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.stage_02 import (
    PromptPreviewRequest, PromptPreviewResult, StructuredCompareRequest,
    StructuredCompareResult, StructuredComparisonItem, StructuredTravelRequest,
    StructuredTravelResult, TravelPlan, TravelValidationRequest,
    TravelValidationResult,
)
from app.services.prompt_service import build_prompt
from app.services.structured_service import generate_structured


stage_02_router = APIRouter(tags=["02 · Prompt와 구조화 출력"])


@stage_02_router.post("/api/prompts/preview", response_model=PromptPreviewResult)
def preview_prompt(payload: PromptPreviewRequest) -> PromptPreviewResult:
    return PromptPreviewResult(**payload.model_dump(), prompt=build_prompt(payload.role, payload.instruction, payload.context, payload.constraint))


@stage_02_router.post("/api/structured/validate", response_model=TravelValidationResult)
def validate_travel_plan(payload: TravelValidationRequest) -> TravelValidationResult:
    try:
        return TravelValidationResult(valid=True, data=TravelPlan.model_validate(payload.payload))
    except ValidationError as error:
        errors = [{"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]} for item in error.errors()]
        return TravelValidationResult(valid=False, errors=errors)


@stage_02_router.post("/api/structured/travel-plan", response_model=StructuredTravelResult)
def create_structured_travel_plan(payload: StructuredTravelRequest) -> StructuredTravelResult:
    selected = payload.provider or settings.llm_provider
    try:
        result = generate_structured(selected, payload.system_prompt, payload.message)
        return StructuredTravelResult(provider=result.provider, model=result.model, content=TravelPlan.model_validate(result.content), latency_ms=result.latency_ms)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} 구조화 출력에 실패했습니다: {error}") from error


@stage_02_router.post("/api/structured/compare", response_model=StructuredCompareResult)
def compare_structured_outputs(payload: StructuredCompareRequest) -> StructuredCompareResult:
    items = []
    for selected in payload.providers:
        try:
            result = generate_structured(selected, payload.system_prompt, payload.message)
            items.append(StructuredComparisonItem(provider=result.provider, status="success", model=result.model, content=TravelPlan.model_validate(result.content), latency_ms=result.latency_ms))
        except Exception as error:
            items.append(StructuredComparisonItem(provider=selected, status="error", error=str(error)))
    return StructuredCompareResult(request_count=len(payload.providers), results=items)
