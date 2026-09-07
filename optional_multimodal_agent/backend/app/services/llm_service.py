from backend.app.core.config import env, openai_client
from backend.app.schemas import AgentAnswer

async def next_step(messages: list[dict], tools: list[dict]):
    async with openai_client() as client:
        result = await client.chat.completions.create(
            model=env("OPENAI_MODEL","gpt-4.1-mini"),messages=messages,tools=tools,
            parallel_tool_calls=False)
    return result.choices[0].message

async def final_answer(messages: list[dict]) -> AgentAnswer:
    async with openai_client() as client:
        result = await client.beta.chat.completions.parse(
            model=env("OPENAI_MODEL","gpt-4.1-mini"),messages=messages,
            response_format=AgentAnswer)
    parsed = result.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("최종 답변을 생성하지 못했습니다.")
    return parsed
