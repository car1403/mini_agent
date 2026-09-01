"""Tool 이름·설명·입력 Schema·실행 함수를 단일 명세로 등록합니다."""

from collections.abc import Callable
from dataclasses import dataclass
from pydantic import BaseModel
from app.schemas import AttractionArgs, HotelArgs, WeatherArgs
from app.tools.travel import get_weather, search_attractions, search_hotels

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    function: Callable[[dict], dict]

    def definition(self) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.input_model.model_json_schema()}

    def execute(self, arguments: dict) -> dict:
        self.input_model.model_validate(arguments)
        return self.function(arguments)

TOOL_REGISTRY = {
    "get_weather": ToolSpec("get_weather", "Open-Meteo에서 특정 도시와 날짜의 실제 예보를 조회합니다.", WeatherArgs, get_weather),
    "search_hotels": ToolSpec("search_hotels", "OpenStreetMap에서 도시의 실제 숙소 위치를 조회합니다. 가격과 예약 가능 여부는 제공하지 않습니다.", HotelArgs, search_hotels),
    "search_attractions": ToolSpec("search_attractions", "OpenStreetMap에서 도시와 분류에 맞는 실제 장소를 조회합니다.", AttractionArgs, search_attractions),
}

def get_tool_definitions() -> list[dict]:
    return [spec.definition() for spec in TOOL_REGISTRY.values()]
