"""날씨·숙소·관광지 조회 Tool의 실제 실행 함수를 구현합니다.

tools.registry에 등록되어 Tool Executor와 Agent/Workflow에서 사용합니다.
"""

from app.schemas import AttractionArgs, HotelArgs, WeatherArgs


def get_weather(args: WeatherArgs) -> dict:
    return {"city": args.city, "date": args.target_date.isoformat(), "condition": "맑음", "temperature_c": 26, "source": "mock"}


def search_hotels(args: HotelArgs) -> dict:
    return {"items": [{"name": "바다 호텔", "price_per_night": 120000}, {"name": "도시 호텔", "price_per_night": 90000}], "query": args.model_dump(mode="json"), "source": "mock"}


def search_attractions(args: AttractionArgs) -> dict:
    return {"items": [{"name": f"{args.city} 바다 박물관", "category": "culture"}, {"name": f"{args.city} 해변 산책로", "category": "nature"}], "category": args.category, "source": "mock"}
