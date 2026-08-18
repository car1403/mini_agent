from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.providers import generate, provider_status
from app.schemas import (
    ConceptCompareResult, GenerateRequest, GenerateResult, MessageRequest,
    ProviderCompareRequest, ProviderCompareResult, ProviderComparisonItem,
    TravelIntentResult,
)
from app.services.concept_service import compare_decisions
from app.services.travel_classifier import classify_travel_request


agent_router = APIRouter(tags=["Agent"])


@agent_router.get("/health")
def health() -> dict:
    return {"status": "ok", "stage": "mini_agent_01_llm", "default_provider": settings.llm_provider}


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
            items.append(ProviderComparisonItem(provider=result.provider, status="success", model=result.model, content=result.content, latency_ms=result.latency_ms))
        except Exception as error:
            items.append(ProviderComparisonItem(provider=selected, status="error", error=str(error)))
    return ProviderCompareResult(request_count=len(payload.providers), results=items)
