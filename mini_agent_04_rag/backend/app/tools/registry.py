"""Tool 이름·설명·입력 Schema·실행 함수를 단일 명세로 등록합니다."""

from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel

from app.schemas import (
    AttractionArgs, HotelArgs, SearchKnowledgeArgs, TopicSearchArgs, WeatherArgs,
)
from app.tools.rag import (
    search_attraction_knowledge, search_flight_knowledge,
    search_hotel_knowledge, search_knowledge_base,
)
from app.tools.travel import get_weather, search_attractions, search_hotels


ToolFunction = Callable[[BaseModel], dict]

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    function: ToolFunction

    def definition(self) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.input_model.model_json_schema()}

    def execute(self, arguments: dict) -> dict:
        validated = self.input_model.model_validate(arguments)
        return self.function(validated)

TOOL_REGISTRY = {
    "get_weather": ToolSpec("get_weather", "특정 도시와 날짜의 교육용 날씨를 조회합니다.", WeatherArgs, get_weather),
    "search_hotels": ToolSpec("search_hotels", "도시, 날짜, 인원에 맞는 교육용 숙소를 조회합니다.", HotelArgs, search_hotels),
    "search_attractions": ToolSpec("search_attractions", "도시와 분류에 맞는 교육용 관광지를 조회합니다.", AttractionArgs, search_attractions),
    "search_knowledge_base": ToolSpec(
        "search_knowledge_base",
        "내부 여행 정책 문서에서 질문과 관련된 근거를 검색합니다. DB나 SQL을 직접 노출하지 않습니다.",
        SearchKnowledgeArgs,
        search_knowledge_base,
    ),
    "search_hotel_knowledge": ToolSpec(
        "search_hotel_knowledge", "호텔 환불·숙박 정책 저장소를 검색합니다.",
        TopicSearchArgs, search_hotel_knowledge,
    ),
    "search_flight_knowledge": ToolSpec(
        "search_flight_knowledge", "항공 수하물·탑승 정책 저장소를 검색합니다.",
        TopicSearchArgs, search_flight_knowledge,
    ),
    "search_attraction_knowledge": ToolSpec(
        "search_attraction_knowledge", "관광지 운영 정보 저장소를 검색합니다.",
        TopicSearchArgs, search_attraction_knowledge,
    ),
}

def get_tool_definitions(names: list[str] | None = None) -> list[dict]:
    if names is None:
        specs = TOOL_REGISTRY.values()
    else:
        unknown = [name for name in names if name not in TOOL_REGISTRY]
        if unknown:
            raise ValueError(f"등록되지 않은 Tool입니다: {', '.join(unknown)}")
        specs = [TOOL_REGISTRY[name] for name in names]
    return [spec.definition() for spec in specs]
