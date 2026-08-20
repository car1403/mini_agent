"""현재·예보 Tool을 Allowlist와 Schema 검증 후 실행하고 답변으로 조립합니다."""

from collections.abc import Callable
from datetime import date, timedelta

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class CurrentWeatherInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)


class WeatherForecastInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)
    target_date: date

    @model_validator(mode="after")
    def validate_target_date(self) -> "WeatherForecastInput":
        today = date.today()
        if self.target_date < today:
            raise ValueError("과거 날짜의 예보는 조회할 수 없습니다.")
        if self.target_date > today + timedelta(days=16):
            raise ValueError("예보는 오늘부터 16일 이내만 조회할 수 있습니다.")
        return self


def get_current_weather(arguments: dict) -> dict:
    args = CurrentWeatherInput.model_validate(arguments)
    return {"city": args.city, "condition": "맑음", "temperature_c": 26, "source": "mock"}


def get_weather_forecast(arguments: dict) -> dict:
    args = WeatherForecastInput.model_validate(arguments)
    return {"city": args.city, "date": args.target_date.isoformat(), "condition": "구름 조금", "temperature_max_c": 27, "source": "mock"}


TOOLS: dict[str, Callable[[dict], dict]] = {
    "get_current_weather": get_current_weather,
    "get_weather_forecast": get_weather_forecast,
}


def run_tool(tool_name: str, arguments: dict) -> dict:
    tool = TOOLS.get(tool_name)
    if tool is None:
        return {"success": False, "error": {"code": "TOOL_NOT_ALLOWED"}}
    try:
        return {"success": True, "tool_name": tool_name, "data": tool(arguments)}
    except ValidationError as error:
        details = [{"field": ".".join(map(str, item["loc"])), "message": item["msg"]} for item in error.errors()]
        return {"success": False, "error": {"code": "TOOL_VALIDATION_ERROR", "details": details}}


def make_final_answer(tool_result: dict) -> str:
    if not tool_result["success"]:
        return "Tool을 실행하지 못했습니다."
    data = tool_result["data"]
    if tool_result["tool_name"] == "get_current_weather":
        return f"현재 {data['city']}은 {data['condition']}, {data['temperature_c']}도입니다."
    return f"{data['date']} {data['city']} 예보는 {data['condition']}, 최고 {data['temperature_max_c']}도입니다."


if __name__ == "__main__":
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    cases = [
        ("get_current_weather", {"city": "부산"}),
        ("get_weather_forecast", {"city": "부산", "target_date": tomorrow}),
        ("get_weather_forecast", {"city": "부산", "target_date": (date.today() - timedelta(days=1)).isoformat()}),
        ("get_weather_forecast", {"city": "부산", "target_date": (date.today() + timedelta(days=17)).isoformat()}),
        ("get_weather_forecast", {"city": "부산", "unknown": True}),
        ("delete_database", {}),
    ]
    for name, arguments in cases:
        result = run_tool(name, arguments)
        print(name, "→", result)
        print("답변 →", make_final_answer(result))
