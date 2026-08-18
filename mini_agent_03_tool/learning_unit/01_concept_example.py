"""Python 함수, Tool Schema, Tool Call, Tool Result를 비교합니다."""

from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    city: str = Field(min_length=1)


def get_weather(arguments: dict) -> dict:
    args = WeatherInput.model_validate(arguments)
    return {"city": args.city, "condition": "맑음", "source": "mock"}


if __name__ == "__main__":
    tool_schema = {
        "name": "get_weather",
        "description": "도시의 교육용 날씨를 조회합니다.",
        "input_schema": WeatherInput.model_json_schema(),
    }
    tool_call = {"name": "get_weather", "arguments": {"city": "부산"}}
    tool_result = get_weather(tool_call["arguments"])

    print("1. Python 함수:", get_weather.__name__)
    print("2. Tool Schema:", tool_schema)
    print("3. Tool Call:", tool_call)
    print("4. Tool Result:", tool_result)
