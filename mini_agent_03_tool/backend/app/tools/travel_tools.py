from collections.abc import Callable

from app.clients.open_meteo_client import fetch_current_weather, fetch_weather_forecast
from app.config import settings
from app.schemas import AttractionArgs, CurrentWeatherArgs, HotelArgs, WeatherForecastArgs


def get_current_weather(arguments: dict) -> dict:
    args = CurrentWeatherArgs.model_validate(arguments)
    if settings.weather_mode == "open_meteo":
        return fetch_current_weather(args.city)
    if settings.weather_mode != "mock":
        raise ValueError(f"지원하지 않는 WEATHER_MODE입니다: {settings.weather_mode}")
    return {"city": args.city, "observed_at": "교육용 현재 시각", "condition": "맑음", "temperature_c": 26, "apparent_temperature_c": 27, "precipitation_mm": 0, "wind_speed_kmh": 8, "source": "mock", "data_type": "mock-current-condition"}


def get_weather_forecast(arguments: dict) -> dict:
    args = WeatherForecastArgs.model_validate(arguments)
    if settings.weather_mode == "open_meteo":
        return fetch_weather_forecast(args.city, args.target_date)
    if settings.weather_mode != "mock":
        raise ValueError(f"지원하지 않는 WEATHER_MODE입니다: {settings.weather_mode}")
    return {"city": args.city, "date": args.target_date.isoformat(), "condition": "구름 조금", "temperature_max_c": 27, "temperature_min_c": 19, "precipitation_probability_percent": 20, "source": "mock", "data_type": "mock-forecast"}


def search_hotels(arguments: dict) -> dict:
    args = HotelArgs.model_validate(arguments)
    return {"items": [{"name": "바다 호텔", "price_per_night": 120000}, {"name": "도시 호텔", "price_per_night": 90000}], "query": args.model_dump(mode="json"), "source": "mock"}


def search_attractions(arguments: dict) -> dict:
    args = AttractionArgs.model_validate(arguments)
    return {"items": [{"name": f"{args.city} 바다 박물관", "category": "culture"}, {"name": f"{args.city} 해변 산책로", "category": "nature"}], "category": args.category, "source": "mock"}


TOOLS: dict[str, Callable[[dict], dict]] = {"get_current_weather": get_current_weather, "get_weather_forecast": get_weather_forecast, "search_hotels": search_hotels, "search_attractions": search_attractions}


def select_tool(message: str) -> dict:
    if any(word in message for word in ("날씨", "비가", "비예보", "기온", "우산")):
        if any(word in message for word in ("내일", "모레", "주말", "예보", "다음 주")):
            return {"tool_name": "get_weather_forecast", "reason": "미래 날씨 예보 요청", "confidence": 0.94}
        return {"tool_name": "get_current_weather", "reason": "현재 날씨 요청", "confidence": 0.94}
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
