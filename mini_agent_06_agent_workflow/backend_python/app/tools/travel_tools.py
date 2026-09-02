from collections.abc import Callable

from app.schemas.models import AttractionArgs, HotelArgs, WeatherArgs


def get_weather(arguments: dict) -> dict:
    args = WeatherArgs.model_validate(arguments)
    return {
        "city": args.city,
        "date": args.target_date.isoformat(),
        "condition": "맑음",
        "temperature_c": 26,
        "source": "mock",
    }


def search_hotels(arguments: dict) -> dict:
    args = HotelArgs.model_validate(arguments)
    return {
        "items": [
            {"name": "바다 호텔", "price_per_night": 120000, "capacity": 4},
            {"name": "도시 호텔", "price_per_night": 90000, "capacity": 2},
        ],
        "query": args.model_dump(mode="json"),
        "source": "mock",
    }


def search_attractions(arguments: dict) -> dict:
    args = AttractionArgs.model_validate(arguments)
    return {
        "items": [
            {"name": f"{args.city} 바다 박물관", "category": "culture"},
            {"name": f"{args.city} 해변 산책로", "category": "nature"},
        ],
        "category": args.category,
        "source": "mock",
    }


TOOLS: dict[str, Callable[[dict], dict]] = {
    "get_weather": get_weather,
    "search_hotels": search_hotels,
    "search_attractions": search_attractions,
}


def select_tool(message: str) -> dict:
    if any(word in message for word in ("날씨", "비", "기온", "우산")):
        return {"tool_name": "get_weather", "reason": "날씨 관련 요청", "confidence": 0.92}
    if any(word in message for word in ("호텔", "숙소", "체크인")):
        return {"tool_name": "search_hotels", "reason": "숙소 관련 요청", "confidence": 0.94}
    if any(word in message for word in ("관광지", "가볼", "명소")):
        return {"tool_name": "search_attractions", "reason": "관광지 관련 요청", "confidence": 0.9}
    return {"tool_name": None, "reason": "필요한 Tool을 확정할 수 없음", "confidence": 0.35}


def run_tool(name: str, arguments: dict) -> dict:
    tool = TOOLS.get(name)
    if tool is None:
        raise PermissionError("허용되지 않은 Tool입니다.")
    return tool(arguments)
