"""Tool의 이름·설명·입력 모델·실행 함수를 단일 명세로 등록합니다.

`tools.executor`, Provider Tool Calling, `/api/tools` 목록 조회에서 사용합니다.
"""

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel

from app.schemas.stage_03 import AttractionArgs, CurrentWeatherArgs, HotelArgs, WeatherForecastArgs
from app.tools.travel import search_attractions, search_hotels
from app.tools.weather import get_current_weather, get_weather_forecast


ToolFunction = Callable[[BaseModel], dict]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    function: ToolFunction

    def definition(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_model.model_json_schema(),
        }

    def execute(self, arguments: dict) -> dict:
        return self.function(self.input_model.model_validate(arguments))


TOOL_REGISTRY: dict[str, ToolSpec] = {
    "get_current_weather": ToolSpec(
        name="get_current_weather",
        description="특정 도시의 현재 기온, 체감 온도, 강수량과 바람을 조회합니다. 미래 날짜 예보에는 사용하지 않습니다.",
        input_model=CurrentWeatherArgs,
        function=get_current_weather,
    ),
    "get_weather_forecast": ToolSpec(
        name="get_weather_forecast",
        description="특정 도시의 내일, 주말 또는 미래 날짜 날씨 예보를 조회합니다. 현재 날씨 질문에는 사용하지 않습니다.",
        input_model=WeatherForecastArgs,
        function=get_weather_forecast,
    ),
    "search_hotels": ToolSpec(
        name="search_hotels",
        description="도시, 날짜, 인원에 맞는 교육용 숙소를 조회합니다.",
        input_model=HotelArgs,
        function=search_hotels,
    ),
    "search_attractions": ToolSpec(
        name="search_attractions",
        description="도시와 분류에 맞는 교육용 관광지를 조회합니다.",
        input_model=AttractionArgs,
        function=search_attractions,
    ),
}


def get_tool_definitions() -> list[dict]:
    return [tool.definition() for tool in TOOL_REGISTRY.values()]
