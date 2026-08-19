from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.config import settings
from app.providers import generate, generate_structured, get_structured_model, provider_status
from app.schemas import (
    ConceptCompareResult, GenerateRequest, GenerateResult, MessageRequest,
    PromptPreviewRequest, PromptPreviewResult, ProviderCompareRequest,
    ProviderCompareResult, ProviderComparisonItem, StructuredCompareRequest,
    StructuredCompareResult, StructuredComparisonItem, StructuredOutputRequest,
    StructuredOutputResult, StructuredValidationRequest,
    StructuredValidationResult, TravelIntentResult,
)
from app.services.concept_service import compare_decisions
from app.services.prompt_service import build_prompt
from app.services.travel_classifier import classify_travel_request


agent_router = APIRouter()

UNIT_01_TAG = "01. LLM to Agent"
UNIT_02_TAG = "02. Prompt & Structured Output"


@agent_router.get("/health", tags=[UNIT_01_TAG])
def health() -> dict:
    return {"status": "ok", "stage": "mini_agent_02_structured_output", "default_provider": settings.llm_provider}


@agent_router.get("/api/providers", tags=[UNIT_01_TAG])
def providers() -> dict:
    return {"default_provider": settings.llm_provider, "providers": provider_status()}


@agent_router.post("/api/concepts/compare", response_model=ConceptCompareResult, tags=[UNIT_01_TAG])
def compare_concepts(payload: MessageRequest) -> ConceptCompareResult:
    return ConceptCompareResult.model_validate(compare_decisions(payload.message))


@agent_router.post("/api/travel/classify", response_model=TravelIntentResult, tags=[UNIT_01_TAG])
def classify_travel(payload: MessageRequest) -> TravelIntentResult:
    return TravelIntentResult.model_validate(classify_travel_request(payload.message))


@agent_router.post("/api/generate", response_model=GenerateResult, tags=[UNIT_01_TAG])
def create_response(payload: GenerateRequest) -> GenerateResult:
    selected = payload.provider or settings.llm_provider
    try:
        return GenerateResult.model_validate(asdict(generate(selected, payload.system_prompt, payload.message)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} 실제 연결에 실패했습니다: {error}") from error


@agent_router.post("/api/providers/compare", response_model=ProviderCompareResult, tags=[UNIT_01_TAG])
def compare_providers(payload: ProviderCompareRequest) -> ProviderCompareResult:
    items: list[ProviderComparisonItem] = []
    for selected in payload.providers:
        try:
            result = generate(selected, payload.system_prompt, payload.message)
            items.append(ProviderComparisonItem(**asdict(result), status="success"))
        except Exception as error:
            items.append(ProviderComparisonItem(provider=selected, status="error", error=str(error)))
    return ProviderCompareResult(request_count=len(payload.providers), results=items)


@agent_router.post("/api/prompts/preview", response_model=PromptPreviewResult, tags=[UNIT_02_TAG])
def preview_prompt(payload: PromptPreviewRequest) -> PromptPreviewResult:
    return PromptPreviewResult(
        **payload.model_dump(),
        prompt=build_prompt(
            payload.role,
            payload.instruction,
            payload.context,
            payload.constraint,
            payload.output_format,
        ),
    )


@agent_router.post("/api/structured/validate", response_model=StructuredValidationResult, tags=[UNIT_02_TAG])
def validate_structured_output(
    payload: StructuredValidationRequest,
) -> StructuredValidationResult:
    try:
        model_class = get_structured_model(payload.schema_type)
        return StructuredValidationResult(
            schema_type=payload.schema_type,
            valid=True,
            data=model_class.model_validate(payload.payload),
        )
    except ValidationError as error:
        errors = [{"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]} for item in error.errors()]
        return StructuredValidationResult(
            schema_type=payload.schema_type, valid=False, errors=errors
        )


@agent_router.post("/api/structured/generate", response_model=StructuredOutputResult, tags=[UNIT_02_TAG])
@agent_router.post(
    "/api/structured/travel-plan",
    response_model=StructuredOutputResult,
    include_in_schema=False,
    tags=[UNIT_02_TAG],
)
def create_structured_output(payload: StructuredOutputRequest) -> StructuredOutputResult:
    selected = payload.provider or settings.llm_provider
    try:
        model_class = get_structured_model(payload.schema_type)
        result = generate_structured(
            selected, payload.system_prompt, payload.message, payload.schema_type
        )
        return StructuredOutputResult(
            provider=result.provider,
            model=result.model,
            schema_type=payload.schema_type,
            content=model_class.model_validate(result.content),
            latency_ms=result.latency_ms,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} 구조화 출력에 실패했습니다: {error}") from error


@agent_router.post("/api/structured/compare", response_model=StructuredCompareResult, tags=[UNIT_02_TAG])
def compare_structured_outputs(payload: StructuredCompareRequest) -> StructuredCompareResult:
    items: list[StructuredComparisonItem] = []
    for selected in payload.providers:
        try:
            model_class = get_structured_model(payload.schema_type)
            result = generate_structured(
                selected, payload.system_prompt, payload.message, payload.schema_type
            )
            items.append(StructuredComparisonItem(provider=result.provider, status="success", model=result.model, schema_type=payload.schema_type, content=model_class.model_validate(result.content), latency_ms=result.latency_ms))
        except Exception as error:
            items.append(StructuredComparisonItem(provider=selected, status="error", schema_type=payload.schema_type, error=str(error)))
    return StructuredCompareResult(request_count=len(payload.providers), results=items)
