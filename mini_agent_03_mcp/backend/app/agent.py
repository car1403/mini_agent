"""HTTP와 stdio MCP Tool을 순차 실행하는 Agent Loop입니다.

전체 흐름
    질문 → 각 MCP Server의 tools/list → Server prefix가 붙은 Tool Schema 생성
    → GPT가 이번 단계에 필요한 Tool 하나 선택
    → Backend가 라우팅 테이블로 원래 Server의 Tool 실행
    → function_call_output을 GPT에 전달하고 반복
    → GPT가 Function Call 없이 답변하면 종료
"""

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .mcp_client import mcp_sessions, result_text
from .schemas import McpRunResult, ToolExecutionTrace


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_AGENT_ROUNDS = 8
INSTRUCTIONS = (
    "당신은 한국 여행 도우미입니다. 질문을 완전히 해결하는 데 필요한 Tool을 "
    "한 단계씩 사용하세요. 호텔 정책을 요청받으면 반드시 먼저 호텔을 검색하고, "
    "검색 결과에서 얻은 hotel_id로 정책을 조회하세요. Tool 결과만 근거로 한국어 "
    "최종 답변을 작성하세요."
)


def to_openai_tool(
    server_name: str,
    tool,
) -> tuple[dict[str, Any], dict[str, str]]:
    """MCP Tool에 Server prefix를 붙이고 라우팅 정보를 만듭니다."""
    public_name = f"{server_name}__{tool.name}"
    raw = tool.model_dump(by_alias=True)
    openai_tool = {
        "type": "function",
        "name": public_name,
        "description": f"[{server_name} MCP Server] {tool.description or ''}",
        "parameters": raw["inputSchema"],
        "strict": False,
    }
    route = {"server": server_name, "tool": tool.name}
    return openai_tool, route


async def run_agent(question: str) -> McpRunResult:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY가 필요합니다.")

    trace: list[ToolExecutionTrace] = []
    llm_calls = 0

    async with AsyncOpenAI() as client, mcp_sessions() as sessions:
        openai_tools: list[dict[str, Any]] = []
        routes: dict[str, dict[str, str]] = {}

        for server_name, session in sessions.items():
            discovered = (await session.list_tools()).tools
            for tool in discovered:
                openai_tool, route = to_openai_tool(server_name, tool)
                openai_tools.append(openai_tool)
                routes[openai_tool["name"]] = route

        previous_response_id: str | None = None
        input_items: str | list[dict[str, str]] = question

        for round_number in range(1, MAX_AGENT_ROUNDS + 1):
            response = await client.responses.create(
                model=OPENAI_MODEL,
                instructions=INSTRUCTIONS,
                input=input_items,
                previous_response_id=previous_response_id,
                tools=openai_tools,
                parallel_tool_calls=False,
            )
            llm_calls += 1
            tool_calls = [
                item for item in response.output if item.type == "function_call"
            ]

            if not tool_calls:
                return McpRunResult(
                    question=question,
                    model=OPENAI_MODEL,
                    available_tools=sorted(routes),
                    llm_calls=llm_calls,
                    trace=trace,
                    answer=response.output_text,
                )

            call = tool_calls[0]
            route = routes.get(call.name)
            if route is None:
                raise ValueError(
                    f"MCP Server가 제공하지 않는 Tool입니다: {call.name}"
                )

            arguments = json.loads(call.arguments)
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments는 JSON Object여야 합니다.")

            result = await sessions[route["server"]].call_tool(
                route["tool"],
                arguments,
            )
            output = result_text(result)
            trace.append(ToolExecutionTrace(
                round=round_number,
                server=route["server"],
                tool=route["tool"],
                public_tool=call.name,
                arguments=arguments,
                is_error=bool(result.isError),
                result=output,
            ))

            tool_output = {
                "server": route["server"],
                "tool": route["tool"],
                "success": not bool(result.isError),
                "content": output,
            }
            previous_response_id = response.id
            input_items = [{
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(tool_output, ensure_ascii=False),
            }]

    raise RuntimeError(
        f"최대 Agent 반복 횟수({MAX_AGENT_ROUNDS})를 초과했습니다."
    )
