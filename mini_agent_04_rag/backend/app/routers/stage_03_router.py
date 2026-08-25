"""Mini Agent 03의 Tool 선택·실행·단일 Agent Cycle API를 제공합니다."""

from dataclasses import asdict
import json

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

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
from app.tools.executor import execute_tool_safely
from app.tools.registry import get_tool_definitions

stage_03_router = APIRouter(tags=["03 · Tool과 Agent"])


@stage_03_router.get("/api/tools")
def tools() -> dict:
    return {
        "tools": get_tool_definitions(),
        "note": (
            "여행 Tool은 조회용 Mock이고 RAG Tool은 실제 pgvector를 사용하는 읽기 전용 검색입니다. "
            "예약·결제·임의 SQL은 실행하지 않습니다."
        ),
    }


@stage_03_router.post("/api/tools/select", response_model=ToolSelectionResult)
def choose_tool(payload: ToolSelectRequest) -> ToolSelectionResult:
    selected = payload.provider or settings.llm_provider
    try:
        return ToolSelectionResult.model_validate(asdict(select_tool(selected, payload.message)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} Tool 선택에 실패했습니다: {error}") from error


@stage_03_router.post("/api/tools/compare", response_model=ToolCompareResult)
def compare_tool_selection(payload: ToolCompareRequest) -> ToolCompareResult:
    items: list[ToolComparisonItem] = []
    for selected in payload.providers:
        try:
            decision = ToolSelectionResult.model_validate(asdict(select_tool(selected, payload.message)))
            items.append(ToolComparisonItem(provider=selected, status="success", decision=decision))
        except Exception as error:
            items.append(ToolComparisonItem(provider=selected, status="error", error=str(error)))
    return ToolCompareResult(request_count=len(payload.providers), results=items)


@stage_03_router.post("/api/tools/run", response_model=ToolRunResult)
def execute_tool(payload: ToolRunRequest) -> ToolRunResult:
    return execute_tool_safely(payload.tool_name, payload.arguments)


@stage_03_router.post("/api/tools/complete", response_model=ToolCompleteResult)
def complete_tool_loop(payload: ToolCompleteRequest) -> ToolCompleteResult:
    selected = payload.provider or settings.llm_provider
    try:
        decision = ToolSelectionResult.model_validate(asdict(select_tool(selected, payload.message)))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"{selected} Tool 선택 실패: {error}") from error

    trace = [{"stage": "1_tool_selection", "data": decision.model_dump(mode="json")}]

    if decision.needs_clarification:
        return ToolCompleteResult(
            provider=selected,
            question=payload.message,
            decision=decision,
            final_answer=decision.follow_up_question,
            trace=trace,
        )

    if decision.tool_name is None:
        return ToolCompleteResult(provider=selected, question=payload.message, decision=decision, final_answer="이 질문에는 실행할 조회 Tool이 필요하지 않습니다.", trace=trace)

    tool_result = execute_tool_safely(decision.tool_name, decision.arguments)
    trace.append({"stage": "2_tool_execution", "data": tool_result.model_dump(mode="json")})
    if not tool_result.success:
        return ToolCompleteResult(provider=selected, question=payload.message, decision=decision, tool_result=tool_result, final_answer="Tool을 안전하게 실행하지 못했습니다. 입력과 권한을 확인해 주세요.", trace=trace)

    if selected == "mock":
        final_answer = f"{decision.tool_name} 조회 결과입니다: {json.dumps(tool_result.data, ensure_ascii=False)}"
    else:
        prompt = f"사용자 질문: {payload.message}\nTool 이름: {decision.tool_name}\nTool Result: {json.dumps(tool_result.data, ensure_ascii=False)}"
        try:
            final_answer = str(generate(selected, "Tool Result에 있는 값만 사용해 친절한 한국어 최종 답변을 작성하세요.", prompt).content)
        except Exception as error:
            final_answer = f"Tool 실행은 성공했지만 최종 답변 생성에 실패했습니다: {error}"

    trace.append({"stage": "3_final_answer", "data": {"text": final_answer}})
    return ToolCompleteResult(provider=selected, question=payload.message, decision=decision, tool_result=tool_result, final_answer=final_answer, trace=trace)
