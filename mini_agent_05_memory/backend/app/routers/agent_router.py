from dataclasses import asdict
import json

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from pydantic import ValidationError

from app.config import settings
from app.media import analyze_image, create_speech
from app.providers import generate, generate_structured, provider_status, select_tool
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
from app.tools.definitions import TRAVEL_TOOL_DEFINITIONS
from app.tools.travel_tools import run_tool


agent_router = APIRouter(tags=["Agent"])


@agent_router.get("/health")
def health() -> dict:
    return {"status": "ok", "stage": "mini_agent_05_memory", "default_provider": settings.llm_provider}


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


@agent_router.post("/api/media/image-analysis")
async def image_analysis(image: UploadFile = File(...), question: str = Form("여행자가 알아야 할 정보와 주의점을 알려주세요.")) -> dict:
    try:
        return analyze_image(image.content_type or "", await image.read(), question).model_dump()
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"이미지 분석 실패: {error}") from error


@agent_router.post("/api/media/tts")
def text_to_speech(payload: TtsRequest) -> Response:
    try:
        return Response(content=create_speech(payload.text, payload.voice, payload.instructions), media_type="audio/mpeg", headers={"X-Synthetic-Voice": "true"})
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"TTS 생성 실패: {error}") from error


@agent_router.get("/api/tools")
def tools() -> dict:
    return {"tools": TRAVEL_TOOL_DEFINITIONS, "note": "모든 Tool은 조회용 Mock이며 실제 예약이나 결제를 실행하지 않습니다."}


@agent_router.post("/api/tools/select", response_model=ToolSelectionResult)
def choose_tool(payload: ToolSelectRequest) -> ToolSelectionResult:
    selected = payload.provider or settings.llm_provider
    try:
        return ToolSelectionResult.model_validate(asdict(select_tool(selected, payload.message)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} Tool 선택에 실패했습니다: {error}") from error


@agent_router.post("/api/tools/compare", response_model=ToolCompareResult)
def compare_tool_selection(payload: ToolCompareRequest) -> ToolCompareResult:
    items: list[ToolComparisonItem] = []
    for selected in payload.providers:
        try:
            decision = ToolSelectionResult.model_validate(asdict(select_tool(selected, payload.message)))
            items.append(ToolComparisonItem(provider=selected, status="success", decision=decision))
        except Exception as error:
            items.append(ToolComparisonItem(provider=selected, status="error", error=str(error)))
    return ToolCompareResult(request_count=len(payload.providers), results=items)


@agent_router.post("/api/tools/run", response_model=ToolRunResult)
def execute_tool(payload: ToolRunRequest) -> ToolRunResult:
    return _run_tool_safely(payload.tool_name, payload.arguments)


def _run_tool_safely(tool_name: str, arguments: dict) -> ToolRunResult:
    try:
        return ToolRunResult(success=True, tool_name=tool_name, data=run_tool(tool_name, arguments))
    except PermissionError as error:
        return ToolRunResult(success=False, tool_name=tool_name, error={"code": "TOOL_NOT_ALLOWED", "message": str(error)})
    except ValidationError as error:
        details = [{"field": ".".join(map(str, item["loc"])), "message": item["msg"], "type": item["type"]} for item in error.errors()]
        return ToolRunResult(success=False, tool_name=tool_name, error={"code": "TOOL_VALIDATION_ERROR", "details": details})
    except Exception as error:
        return ToolRunResult(success=False, tool_name=tool_name, error={"code": "TOOL_EXECUTION_ERROR", "message": str(error)})


@agent_router.post("/api/tools/complete", response_model=ToolCompleteResult)
def complete_tool_loop(payload: ToolCompleteRequest) -> ToolCompleteResult:
    selected = payload.provider or settings.llm_provider
    try:
        decision = ToolSelectionResult.model_validate(asdict(select_tool(selected, payload.message)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} Tool 선택 실패: {error}") from error

    if decision.tool_name is None:
        return ToolCompleteResult(provider=selected, question=payload.message, decision=decision, final_answer="이 질문에는 실행할 조회 Tool이 필요하지 않습니다.")

    tool_result = _run_tool_safely(decision.tool_name, decision.arguments)
    if not tool_result.success:
        return ToolCompleteResult(provider=selected, question=payload.message, decision=decision, tool_result=tool_result, final_answer="Tool을 안전하게 실행하지 못했습니다. 입력과 권한을 확인해 주세요.")

    if selected == "mock":
        final_answer = f"{decision.tool_name} 조회 결과입니다: {json.dumps(tool_result.data, ensure_ascii=False)}"
    else:
        prompt = f"사용자 질문: {payload.message}\nTool 이름: {decision.tool_name}\nTool Result: {json.dumps(tool_result.data, ensure_ascii=False)}"
        try:
            final_answer = str(generate(selected, "Tool Result에 있는 값만 사용해 친절한 한국어 최종 답변을 작성하세요.", prompt).content)
        except Exception as error:
            final_answer = f"Tool 실행은 성공했지만 최종 답변 생성에 실패했습니다: {error}"

    return ToolCompleteResult(provider=selected, question=payload.message, decision=decision, tool_result=tool_result, final_answer=final_answer)
