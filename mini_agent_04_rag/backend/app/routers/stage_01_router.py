"""Mini Agent 01의 LLM·Provider·분류·Media API를 제공합니다."""

from dataclasses import asdict
import json

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from pydantic import ValidationError

from app.core.config import settings
from app.services.image_analysis_service import analyze_image
from app.services.speech_service import create_speech
from app.agents.tool_selector import select_tool
from app.providers.registry import provider_status
from app.services.generation_service import generate
from app.services.structured_service import generate_structured
from app.schemas import (
    ConceptCompareResult, GenerateRequest, GenerateResult, MessageRequest,
    PromptPreviewRequest, PromptPreviewResult, ProviderCompareRequest,
    ProviderCompareResult, ProviderComparisonItem, StructuredCompareRequest,
    StructuredCompareResult, StructuredComparisonItem, StructuredTravelRequest,
    StructuredTravelResult, ToolCompareRequest, ToolCompareResult,
    ToolComparisonItem, ToolCompleteRequest, ToolCompleteResult,
    ToolRunRequest, ToolRunResult, ToolSelectRequest,
    ToolSelectionResult, TravelIntentResult, TravelPlan, TravelValidationRequest,
    TravelValidationResult, TtsRequest,
)
from app.services.concept_service import compare_decisions
from app.services.prompt_service import build_prompt
from app.services.travel_classifier import classify_travel_request
from app.tools.executor import run_tool
from app.tools.registry import get_tool_definitions

stage_01_router = APIRouter(tags=["01 · LLM 기초"])


@stage_01_router.get("/health")
def health() -> dict:
    return {"status": "ok", "stage": "mini_agent_04_rag", "default_provider": settings.llm_provider}


@stage_01_router.get("/api/providers")
def providers() -> dict:
    return {"default_provider": settings.llm_provider, "providers": provider_status()}


@stage_01_router.post("/api/concepts/compare", response_model=ConceptCompareResult)
def compare_concepts(payload: MessageRequest) -> ConceptCompareResult:
    return ConceptCompareResult.model_validate(compare_decisions(payload.message))


@stage_01_router.post("/api/travel/classify", response_model=TravelIntentResult)
def classify_travel(payload: MessageRequest) -> TravelIntentResult:
    return TravelIntentResult.model_validate(classify_travel_request(payload.message))


@stage_01_router.post("/api/generate", response_model=GenerateResult)
def create_response(payload: GenerateRequest) -> GenerateResult:
    selected = payload.provider or settings.llm_provider
    try:
        return GenerateResult.model_validate(asdict(generate(selected, payload.system_prompt, payload.message)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} 실제 연결에 실패했습니다: {error}") from error


@stage_01_router.post("/api/providers/compare", response_model=ProviderCompareResult)
def compare_providers(payload: ProviderCompareRequest) -> ProviderCompareResult:
    items: list[ProviderComparisonItem] = []
    for selected in payload.providers:
        try:
            result = generate(selected, payload.system_prompt, payload.message)
            items.append(ProviderComparisonItem(**asdict(result), status="success"))
        except Exception as error:
            items.append(ProviderComparisonItem(provider=selected, status="error", error=str(error)))
    return ProviderCompareResult(request_count=len(payload.providers), results=items)


@stage_01_router.post("/api/media/image-analysis")
async def image_analysis(image: UploadFile = File(...), question: str = Form("여행자가 알아야 할 정보와 주의점을 알려주세요.")) -> dict:
    try:
        return analyze_image(image.content_type or "", await image.read(), question).model_dump()
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"이미지 분석 실패: {error}") from error


@stage_01_router.post("/api/media/tts")
def text_to_speech(payload: TtsRequest) -> Response:
    try:
        return Response(content=create_speech(payload.text, payload.voice, payload.instructions), media_type="audio/mpeg", headers={"X-Synthetic-Voice": "true"})
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"TTS 생성 실패: {error}") from error
