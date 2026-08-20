"""Open-Meteo 응답을 Mini Agent의 공통 날씨 데이터로 정규화합니다."""

from datetime import date
from typing import Any

import httpx

from app.config import settings


WEATHER_CODES = {0: "맑음", 1: "대체로 맑음", 2: "부분적으로 흐림", 3: "흐림", 45: "안개", 51: "약한 이슬비", 53: "이슬비", 55: "강한 이슬비", 61: "약한 비", 63: "비", 65: "강한 비", 71: "약한 눈", 73: "눈", 75: "강한 눈", 80: "약한 소나기", 81: "소나기", 82: "강한 소나기", 95: "뇌우"}
KOREAN_CITY_ALIASES = {"서울": "Seoul", "부산": "Busan", "제주": "Jeju", "강릉": "Gangneung"}


def _get(path: str, params: dict[str, Any], *, geocoding: bool = False) -> dict:
    base_url = settings.open_meteo_geocoding_url if geocoding else settings.open_meteo_base_url
    response = httpx.get(f"{base_url}{path}", params=params, timeout=settings.request_timeout_seconds)
    response.raise_for_status()
    return response.json()


def geocode_city(city: str) -> dict:
    search_name = KOREAN_CITY_ALIASES.get(city.strip(), city.strip())
    body = _get("/v1/search", {"name": search_name, "count": 10, "language": "ko", "countryCode": "KR"}, geocoding=True)
    results = body.get("results", [])
    if not results:
        raise ValueError(f"대한민국 도시를 찾을 수 없습니다: {city}")
    populated_places = [item for item in results if str(item.get("feature_code", "")).startswith("PPL")]
    candidates = populated_places or results
    location = max(candidates, key=lambda item: int(item.get("population") or 0))
    return {"requested_city": city, "name": location["name"], "admin1": location.get("admin1", ""), "latitude": location["latitude"], "longitude": location["longitude"]}


def fetch_current_weather(city: str) -> dict:
    location = geocode_city(city)
    body = _get("/v1/forecast", {"latitude": location["latitude"], "longitude": location["longitude"], "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m", "timezone": "Asia/Seoul"})
    current = body["current"]
    code = int(current["weather_code"])
    return {"city": location["name"], "admin1": location["admin1"], "observed_at": current["time"], "condition": WEATHER_CODES.get(code, f"날씨 코드 {code}"), "temperature_c": current["temperature_2m"], "apparent_temperature_c": current["apparent_temperature"], "precipitation_mm": current["precipitation"], "wind_speed_kmh": current["wind_speed_10m"], "source": "open-meteo", "data_type": "model-based-current-condition"}


def fetch_weather_forecast(city: str, target_date: date) -> dict:
    location = geocode_city(city)
    body = _get("/v1/forecast", {"latitude": location["latitude"], "longitude": location["longitude"], "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max", "start_date": target_date.isoformat(), "end_date": target_date.isoformat(), "timezone": "Asia/Seoul"})
    daily = body["daily"]
    if not daily.get("time"):
        raise ValueError(f"예보 결과가 없습니다: {target_date.isoformat()}")
    code = int(daily["weather_code"][0])
    return {"city": location["name"], "admin1": location["admin1"], "date": daily["time"][0], "condition": WEATHER_CODES.get(code, f"날씨 코드 {code}"), "temperature_max_c": daily["temperature_2m_max"][0], "temperature_min_c": daily["temperature_2m_min"][0], "precipitation_probability_percent": daily["precipitation_probability_max"][0], "source": "open-meteo", "data_type": "forecast"}
