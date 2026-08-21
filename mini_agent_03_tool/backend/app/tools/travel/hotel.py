"""도시·숙박일·인원 조건을 검증하는 교육용 호텔 검색 Tool을 구현합니다.

`tools.registry`에 등록되어 Tool Executor와 Agent Cycle에서 사용합니다.
"""

from app.schemas.stage_03 import HotelArgs


def search_hotels(args: HotelArgs) -> dict:
    return {"items": [{"name": "바다 호텔", "price_per_night": 120000}, {"name": "도시 호텔", "price_per_night": 90000}], "query": args.model_dump(mode="json"), "source": "mock"}
