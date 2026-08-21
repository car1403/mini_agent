"""도시와 분류에 맞는 교육용 관광지 검색 Tool을 구현합니다.

`tools.registry`에 등록되어 Tool Executor와 Agent Cycle에서 사용합니다.
"""

from app.schemas.stage_03 import AttractionArgs


def search_attractions(args: AttractionArgs) -> dict:
    return {"items": [{"name": f"{args.city} 바다 박물관", "category": "culture"}, {"name": f"{args.city} 해변 산책로", "category": "nature"}], "category": args.category, "source": "mock"}
