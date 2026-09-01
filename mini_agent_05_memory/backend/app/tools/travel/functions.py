"""날씨·숙소·관광지 조회 Tool의 실제 실행 함수를 구현합니다.

tools.registry에 등록되어 Tool Executor와 Agent/Workflow에서 사용합니다.
"""

import httpx

from app.schemas import AttractionArgs, HotelArgs, WeatherArgs


def _geocode(city: str) -> dict:
    response = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "ko", "format": "json"},
        timeout=15,
    )
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        raise ValueError(f"도시를 찾을 수 없습니다: {city}")
    return results[0]


def _nominatim(query: str, limit: int = 5) -> list[dict]:
    response = httpx.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": query, "format": "jsonv2", "limit": limit, "accept-language": "ko"},
        headers={"User-Agent": "mini-agent-memory-course/1.0"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def get_weather(arguments: dict) -> dict:
    args = WeatherArgs.model_validate(arguments)
    location = _geocode(args.city)
    target_date = args.target_date.isoformat()
    response = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
            "start_date": target_date,
            "end_date": target_date,
        },
        timeout=20,
    )
    response.raise_for_status()
    daily = response.json().get("daily") or {}
    if not daily.get("time"):
        raise RuntimeError("Open-Meteo가 해당 날짜의 예보를 반환하지 않았습니다.")
    return {
        "city": location["name"],
        "date": daily["time"][0],
        "weather_code": daily["weather_code"][0],
        "temperature_max_c": daily["temperature_2m_max"][0],
        "temperature_min_c": daily["temperature_2m_min"][0],
        "precipitation_probability_max": daily["precipitation_probability_max"][0],
        "source": "Open-Meteo",
    }


def search_hotels(arguments: dict) -> dict:
    args = HotelArgs.model_validate(arguments)
    places = _nominatim(f"hotel in {args.city}")
    return {
        "items": [
            {"name": item.get("name") or item.get("display_name"), "display_name": item.get("display_name"), "latitude": item.get("lat"), "longitude": item.get("lon")}
            for item in places
        ],
        "query": args.model_dump(mode="json"),
        "notice": "위치 검색 결과이며 객실 가격과 예약 가능 여부는 제공하지 않습니다.",
        "source": "OpenStreetMap Nominatim",
    }


def search_attractions(arguments: dict) -> dict:
    args = AttractionArgs.model_validate(arguments)
    category_query = {"nature": "park", "culture": "museum", "food": "restaurant", "all": "tourist attraction"}[args.category]
    places = _nominatim(f"{category_query} in {args.city}")
    return {
        "items": [
            {"name": item.get("name") or item.get("display_name"), "display_name": item.get("display_name"), "latitude": item.get("lat"), "longitude": item.get("lon")}
            for item in places
        ],
        "category": args.category,
        "source": "OpenStreetMap Nominatim",
    }
