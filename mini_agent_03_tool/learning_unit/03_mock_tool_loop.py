"""System·User Message부터 Tool Result 기반 최종 답변까지 Mock Loop로 실행합니다."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class CurrentWeatherInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1, description="현재 날씨를 조회할 도시")


def get_current_weather(arguments: dict[str, Any]) -> dict[str, Any]:
    args = CurrentWeatherInput.model_validate(arguments)
    return {"city": args.city, "condition": "맑음", "temperature_c": 26, "source": "mock"}


TOOL_SCHEMAS = [
    {
        "name": "get_current_weather",
        "description": "특정 도시의 현재 날씨와 기온을 조회합니다.",
        "input_schema": CurrentWeatherInput.model_json_schema(),
    }
]
TOOLS = {"get_current_weather": get_current_weather}


def mock_llm(messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
    """첫 호출에는 Tool Call, Tool Result 이후 호출에는 최종 답변을 반환합니다."""
    last_message = messages[-1]
    if last_message["role"] == "tool":
        data = last_message["content"]
        return {
            "type": "final_answer",
            "content": f"현재 {data['city']}은 {data['condition']}이며 기온은 {data['temperature_c']}도입니다.",
        }

    user_message = next(message["content"] for message in reversed(messages) if message["role"] == "user")
    available_tools = {tool["name"] for tool in tools}
    if any(word in user_message for word in ("날씨", "기온", "비", "우산")):
        city = next((name for name in ("서울", "부산", "제주", "강릉") if name in user_message), None)
        if city is None:
            return {"type": "final_answer", "content": "현재 날씨를 확인할 도시를 알려주세요."}
        if "get_current_weather" in available_tools:
            return {"type": "tool_call", "id": "call_weather_001", "name": "get_current_weather", "arguments": {"city": city}}
    return {"type": "final_answer", "content": "이 질문에는 실행할 Tool이 필요하지 않습니다."}


def execute_tool(tool_call: dict[str, Any]) -> dict[str, Any]:
    tool = TOOLS.get(tool_call["name"])
    if tool is None:
        return {"success": False, "error": {"code": "TOOL_NOT_ALLOWED"}}
    try:
        return {"success": True, "tool_name": tool_call["name"], "tool_call_id": tool_call["id"], "data": tool(tool_call["arguments"])}
    except ValidationError as error:
        return {"success": False, "error": {"code": "TOOL_VALIDATION_ERROR", "details": error.errors()}}


def run_mock_agent(system_message: str, user_message: str) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    trace: list[dict[str, Any]] = [{"stage": "input_messages", "data": messages.copy()}]

    first_response = mock_llm(messages, TOOL_SCHEMAS)
    trace.append({"stage": "first_llm_response", "data": first_response})
    if first_response["type"] == "final_answer":
        return {"messages": messages, "tool_result": None, "final_answer": first_response["content"], "trace": trace}

    messages.append({"role": "assistant", "tool_call": first_response})
    execution = execute_tool(first_response)
    trace.append({"stage": "tool_execution", "data": execution})
    if not execution["success"]:
        return {"messages": messages, "tool_result": execution, "final_answer": "Tool을 안전하게 실행하지 못했습니다.", "trace": trace}

    messages.append({"role": "tool", "tool_call_id": execution["tool_call_id"], "name": execution["tool_name"], "content": execution["data"]})
    second_response = mock_llm(messages, TOOL_SCHEMAS)
    trace.append({"stage": "second_llm_response", "data": second_response})
    messages.append({"role": "assistant", "content": second_response["content"]})
    return {"messages": messages, "tool_result": execution, "final_answer": second_response["content"], "trace": trace}


if __name__ == "__main__":
    result = run_mock_agent(
        system_message="당신은 여행 도우미입니다. Tool Result에 없는 사실은 추측하지 마세요.",
        user_message="현재 부산 날씨와 기온을 알려주세요.",
    )
    for index, item in enumerate(result["trace"], start=1):
        print(f"\n{index}. {item['stage']}")
        print(item["data"])
    print("\n최종 답변:", result["final_answer"])
