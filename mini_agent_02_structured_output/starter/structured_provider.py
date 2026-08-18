"""TODO 4: 먼저 Mock 결과를 Schema로 검증한 뒤 실제 Provider로 확장하세요."""

from travel_plan_schema import TravelPlan


MOCK_OUTPUT = {
    "destination": "부산",
    "summary": "대표 장소를 둘러보는 교육용 일정",
    "recommended_days": 3,
    "activities": ["지역 명소 방문", "현지 음식 체험"],
    "cautions": ["운영 시간을 확인하세요."],
}


# TODO: MOCK_OUTPUT을 TravelPlan으로 검증하고 JSON으로 출력하세요.
