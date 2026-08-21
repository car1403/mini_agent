"""여러 도메인 Agent가 재사용할 수 있는 가장 작은 실행 흐름입니다.

학생은 이 파일 하나에서 다음 순서를 따라갈 수 있습니다.

1. LLM이 Tool 이름과 arguments를 선택한다.
2. Python이 선택된 Tool을 실행한다.
3. LLM이 Tool Result를 자연어 답변으로 바꾼다.

도메인의 역할·지침·Tool 목록은 이 파일이 아니라 각 도메인 Agent가 제공합니다.
"""

import json
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from app.core.config import settings
from app.schemas.stage_03 import ToolCompleteResult, ToolRunResult, ToolSelectionResult
from app.tools.executor import execute_tool_safely


@dataclass
class ToolDecision:
    """LLM이 선택한 Tool과 실행 전 검사 결과입니다."""

    provider: str
    model: str
    tool_name: str | None
    arguments: dict[str, Any]
    reason: str
    confidence: float
    latency_ms: int
    missing_arguments: list[str] = field(default_factory=list)
    needs_clarification: bool = False
    follow_up_question: str = ""
    raw_tool_call: dict[str, Any] | None = None


def _openai_client():
    """API 키를 확인하고 OpenAI SDK Client를 만듭니다."""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

    from openai import OpenAI

    return OpenAI(api_key=settings.openai_api_key)


def select_tool(
    message: str,
    instructions: str,
    tools: list[dict[str, Any]],
    tool_choice: str = "auto",
) -> ToolDecision:
    """첫 번째 단계: OpenAI가 사용할 Tool과 arguments를 선택합니다."""
    if tool_choice == "none":
        return ToolDecision("openai", "tool-choice-none", None, {}, "Tool 사용 금지", 1.0, 0)

    decision = _select_tool_with_openai(message, instructions, tools, tool_choice)
    return _check_required_arguments(decision, tools)


def _select_tool_with_openai(
    message: str,
    instructions: str,
    tools: list[dict[str, Any]],
    tool_choice: str,
) -> ToolDecision:
    """실제 LLM 호출 지점: OpenAI에게 질문과 Tool 목록을 함께 전달합니다."""
    openai_tools = [
        {
            "type": "function",
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        }
        for tool in tools
    ]

    started = perf_counter()

    # 첫 번째 LLM 호출: 답변을 쓰는 대신 사용할 Tool과 arguments를 고릅니다.
    response = _openai_client().responses.create(
        model=settings.openai_model,
        instructions=instructions,
        input=message,
        tools=openai_tools,
        tool_choice=tool_choice,
    )

    tool_call = next(
        (item for item in response.output if item.type == "function_call"),
        None,
    )
    arguments = json.loads(tool_call.arguments) if tool_call else {}

    return ToolDecision(
        provider="openai",
        model=settings.openai_model,
        tool_name=tool_call.name if tool_call else None,
        arguments=arguments,
        reason="OpenAI가 질문과 Tool 설명을 보고 선택한 결과",
        confidence=0.9 if tool_call else 0.4,
        latency_ms=round((perf_counter() - started) * 1000),
        raw_tool_call={"name": tool_call.name, "arguments": tool_call.arguments} if tool_call else None,
    )


def _check_required_arguments(decision: ToolDecision, tools: list[dict[str, Any]]) -> ToolDecision:
    """두 번째 단계 전 검사: Tool 실행에 필요한 값이 모두 있는지 확인합니다."""
    definitions = {tool["name"]: tool for tool in tools}
    schema = definitions.get(decision.tool_name or "", {}).get("input_schema", {})
    missing = [name for name in schema.get("required", []) if name not in decision.arguments]
    decision.missing_arguments = missing
    decision.needs_clarification = bool(missing)
    decision.follow_up_question = f"Tool 실행 전에 다음 정보를 알려주세요: {', '.join(missing)}" if missing else ""
    return decision


def run_agent(
    message: str,
    instructions: str,
    final_answer_instructions: str,
    tools: list[dict[str, Any]],
    tool_choice: str = "auto",
) -> ToolCompleteResult:
    """선택 → 실행 → 최종 답변의 단일 Agent Cycle을 순서대로 실행합니다."""
    raw_decision = select_tool(message, instructions, tools, tool_choice)
    decision = ToolSelectionResult.model_validate(raw_decision.__dict__)
    trace = [{"stage": "1_tool_selection", "data": decision.model_dump(mode="json")}]

    if decision.needs_clarification:
        return ToolCompleteResult(
            provider="openai",
            question=message,
            decision=decision,
            final_answer=decision.follow_up_question,
            trace=trace,
        )

    if decision.tool_name is None:
        return ToolCompleteResult(
            provider="openai",
            question=message,
            decision=decision,
            final_answer="이 질문에는 실행할 조회 Tool이 필요하지 않습니다.",
            trace=trace,
        )

    # 두 번째 단계: LLM이 아니라 Python Backend가 실제 함수를 실행합니다.
    tool_result = execute_tool_safely(decision.tool_name, decision.arguments)
    trace.append({"stage": "2_tool_execution", "data": tool_result.model_dump(mode="json")})
    if not tool_result.success:
        return ToolCompleteResult(
            provider="openai",
            question=message,
            decision=decision,
            tool_result=tool_result,
            final_answer="Tool을 안전하게 실행하지 못했습니다. 입력값을 확인해 주세요.",
            trace=trace,
        )

    final_answer = _make_final_answer(message, tool_result, final_answer_instructions)
    trace.append({"stage": "3_final_answer", "data": {"text": final_answer}})
    return ToolCompleteResult(
        provider="openai",
        question=message,
        decision=decision,
        tool_result=tool_result,
        final_answer=final_answer,
        trace=trace,
    )


def _make_final_answer(
    question: str,
    tool_result: ToolRunResult,
    instructions: str,
) -> str:
    """세 번째 단계: Tool Result를 사용자가 읽을 자연어 답변으로 바꿉니다."""
    prompt = (
        f"사용자 질문: {question}\n"
        f"Tool 이름: {tool_result.tool_name}\n"
        f"Tool Result: {json.dumps(tool_result.data, ensure_ascii=False)}"
    )

    # 두 번째 LLM 호출: Tool Result에 있는 정보만 사용해 최종 답변을 씁니다.
    response = _openai_client().responses.create(
        model=settings.openai_model,
        instructions=instructions,
        input=prompt,
    )
    return response.output_text
