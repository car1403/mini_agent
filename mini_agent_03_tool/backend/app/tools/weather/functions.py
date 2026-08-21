"""날씨 입력을 검증하고 Mock 또는 Open-Meteo 실행 경로를 선택합니다.

`tools.registry`에 등록되어 Tool Executor와 Agent Cycle에서 사용합니다.
"""

from app.core.config import settings
from app.schemas.stage_03 import CurrentWeatherArgs, WeatherForecastArgs
from app.tools.weather.open_meteo import fetch_current_weather, fetch_weather_forecast


def get_current_weather(args: CurrentWeatherArgs) -> dict:
    if settings.weather_mode == "open_meteo":
        return fetch_current_weather(args.city)
    if settings.weather_mode != "mock":
        raise ValueError(f"지원하지 않는 WEATHER_MODE입니다: {settings.weather_mode}")
    return {"city": args.city, "observed_at": "교육용 현재 시각", "condition": "맑음", "temperature_c": 26, "apparent_temperature_c": 27, "precipitation_mm": 0, "wind_speed_kmh": 8, "source": "mock", "data_type": "mock-current-condition"}


def get_weather_forecast(args: WeatherForecastArgs) -> dict:
    if settings.weather_mode == "open_meteo":
        return fetch_weather_forecast(args.city, args.target_date)
    if settings.weather_mode != "mock":
        raise ValueError(f"지원하지 않는 WEATHER_MODE입니다: {settings.weather_mode}")
    return {"city": args.city, "date": args.target_date.isoformat(), "condition": "구름 조금", "temperature_max_c": 27, "temperature_min_c": 19, "precipitation_probability_percent": 20, "source": "mock", "data_type": "mock-forecast"}
