from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.config import settings
from app.providers import generate, generate_structured, provider_status
from app.schemas import (
    ConceptCompareResult, GenerateRequest, GenerateResult, MessageRequest,
    PromptPreviewRequest, PromptPreviewResult, ProviderCompareRequest,
    ProviderCompareResult, ProviderComparisonItem, StructuredCompareRequest,
    StructuredCompareResult, StructuredComparisonItem, StructuredTravelRequest,
    StructuredTravelResult, TravelIntentResult, TravelPlan,
    TravelValidationRequest, TravelValidationResult,
)
from app.services.concept_service import compare_decisions
from app.services.prompt_service import build_prompt
from app.services.travel_classifier import classify_travel_request


agent_router = APIRouter(tags=["Agent"])


@agent_router.get("/health")
def health() -> dict:
    return {"status": "ok", "stage": "mini_agent_02_structured_output", "default_provider": settings.llm_provider}


@agent_router.get("/api/providers")
def providers() -> dict:
    return {"default_provider": settings.llm_provider, "providers": provider_status()}


@agent_router.post("/api/concepts/compare", response_model=ConceptCompareResult)
def compare_concepts(payload: MessageRequest) -> ConceptCompareResult:
    return ConceptCompareResult.model_validate(compare_decisions(payload.message))


@agent_router.post("/api/travel/classify", response_model=TravelIntentResult)
def classify_travel(payload: MessageRequest) -> TravelIntentResult:
    return TravelIntentResult.model_validate(classify_travel_request(payload.message))


@agent_router.post("/api/generate", response_model=GenerateResult)
def create_response(payload: GenerateRequest) -> GenerateResult:
    selected = payload.provider or settings.llm_provider
    try:
        return GenerateResult.model_validate(asdict(generate(selected, payload.system_prompt, payload.message)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} 실제 연결에 실패했습니다: {error}") from error


@agent_router.post("/api/providers/compare", response_model=ProviderCompareResult)
def compare_providers(payload: ProviderCompareRequest) -> ProviderCompareResult:
    items: list[ProviderComparisonItem] = []
    for selected in payload.providers:
        try:
            result = generate(selected, payload.system_prompt, payload.message)
            items.append(ProviderComparisonItem(**asdict(result), status="success"))
        except Exception as error:
            items.append(ProviderComparisonItem(provider=selected, status="error", error=str(error)))
    return ProviderCompareResult(request_count=len(payload.providers), results=items)


@agent_router.post("/api/prompts/preview", response_model=PromptPreviewResult)
def preview_prompt(payload: PromptPreviewRequest) -> PromptPreviewResult:
    return PromptPreviewResult(**payload.model_dump(), prompt=build_prompt(payload.role, payload.instruction, payload.context, payload.constraint))


@agent_router.post("/api/structured/validate", response_model=TravelValidationResult)
def validate_travel_plan(payload: TravelValidationRequest) -> TravelValidationResult:
    try:
        return TravelValidationResult(valid=True, data=TravelPlan.model_validate(payload.payload))
    except ValidationError as error:
        errors = [{"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]} for item in error.errors()]
        return TravelValidationResult(valid=False, errors=errors)


@agent_router.post("/api/structured/travel-plan", response_model=StructuredTravelResult)
def create_structured_travel_plan(payload: StructuredTravelRequest) -> StructuredTravelResult:
    selected = payload.provider or settings.llm_provider
    try:
        result = generate_structured(selected, payload.system_prompt, payload.message)
        return StructuredTravelResult(provider=result.provider, model=result.model, content=TravelPlan.model_validate(result.content), latency_ms=result.latency_ms)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} 구조화 출력에 실패했습니다: {error}") from error


@agent_router.post("/api/structured/compare", response_model=StructuredCompareResult)
def compare_structured_outputs(payload: StructuredCompareRequest) -> StructuredCompareResult:
    items: list[StructuredComparisonItem] = []
    for selected in payload.providers:
        try:
            result = generate_structured(selected, payload.system_prompt, payload.message)
            items.append(StructuredComparisonItem(provider=result.provider, status="success", model=result.model, content=TravelPlan.model_validate(result.content), latency_ms=result.latency_ms))
        except Exception as error:
            items.append(StructuredComparisonItem(provider=selected, status="error", error=str(error)))
    return StructuredCompareResult(request_count=len(payload.providers), results=items)
