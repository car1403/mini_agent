from typing import Any

from openai import AsyncOpenAI

from app.core.config import OPENAI_MODEL, require_openai_api_key


def create_client() -> AsyncOpenAI:
    require_openai_api_key()
    return AsyncOpenAI()


async def first_response(
    client: AsyncOpenAI,
    question: str,
    instructions: str,
    tools: list[dict[str, Any]],
) -> Any:
    return await client.responses.create(
        model=OPENAI_MODEL,
        instructions=instructions,
        input=question,
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=False,
    )


async def next_response(
    client: AsyncOpenAI,
    previous_response_id: str,
    tool_outputs: list[dict[str, Any]],
    instructions: str,
    tools: list[dict[str, Any]],
) -> Any:
    return await client.responses.create(
        model=OPENAI_MODEL,
        instructions=instructions,
        previous_response_id=previous_response_id,
        input=tool_outputs,
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=False,
    )
