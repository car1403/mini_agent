"""GPT가 HTTP MCP Tool을 선택하고 결과를 종합하는 2단계 실행 구조입니다.

전체 흐름
    질문 → MCP tools/list → MCP Schema를 OpenAI Function Tool로 변환
    → 첫 번째 GPT 호출에서 필요한 Tool들을 선택
    → Backend가 같은 MCP Session에서 모든 Tool을 순서대로 호출
    → function_call_output을 call_id와 함께 두 번째 GPT 호출에 전달
    → GPT가 Tool 결과만 근거로 최종 한국어 답변 생성

날씨와 호텔은 서로 의존하지 않으므로 반복 Agent Loop를 사용하지 않습니다.
"""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .mcp_client import result_text, travel_session
from .schemas import McpRunResult, ToolExecutionTrace


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
INSTRUCTIONS = (
    "당신은 한국 여행 도우미입니다. 사용자 요청에 필요한 Tool을 모두 선택하세요. "
    "날씨와 호텔을 함께 요청하면 두 Tool을 모두 호출하세요. Tool 결과만 근거로 "
    "한국어 최종 답변을 작성하세요."
)


def to_openai_tool(tool) -> dict[str, Any]:
    raw = tool.model_dump(by_alias=True)
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": raw["inputSchema"],
        "strict": False,
    }


async def run_agent(question: str) -> McpRunResult:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY가 필요합니다.")

    trace: list[ToolExecutionTrace] = []
    async with AsyncOpenAI() as client, travel_session() as session:
        discovered = (await session.list_tools()).tools
        available = {tool.name for tool in discovered}
        openai_tools = [to_openai_tool(tool) for tool in discovered]
        response = await client.responses.create(
            model=OPENAI_MODEL,
            instructions=INSTRUCTIONS,
            input=question,
            tools=openai_tools,
            parallel_tool_calls=True,
        )

        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            return McpRunResult(
                question=question,
                model=OPENAI_MODEL,
                available_tools=sorted(available),
                llm_calls=1,
                trace=trace,
                answer=response.output_text,
            )

        tool_outputs = []
        for call in tool_calls:
            if call.name not in available:
                raise ValueError(f"MCP Server가 제공하지 않는 Tool입니다: {call.name}")
            arguments = json.loads(call.arguments)
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments는 JSON Object여야 합니다.")

            result = await session.call_tool(call.name, arguments)
            output = result_text(result)
            trace.append(ToolExecutionTrace(
                tool=call.name,
                arguments=arguments,
                is_error=bool(result.isError),
                result=output,
            ))
            tool_outputs.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": output,
            })

        final_response = await client.responses.create(
            model=OPENAI_MODEL,
            instructions=INSTRUCTIONS,
            previous_response_id=response.id,
            input=tool_outputs,
        )
        return McpRunResult(
            question=question,
            model=OPENAI_MODEL,
            available_tools=sorted(available),
            llm_calls=2,
            trace=trace,
            answer=final_response.output_text,
        )
