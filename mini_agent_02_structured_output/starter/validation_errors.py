"""TODO 3: 정상·오류 payload를 검증하고 오류 필드와 메시지를 출력하세요."""

from pydantic import ValidationError

from travel_plan_schema import TravelPlan


PAYLOAD = {
    "destination": "부산",
    "summary": "대중교통 중심 여행",
    "recommended_days": 0,
    "activities": [],
    "cautions": [],
}


try:
    # TODO: TravelPlan.model_validate()로 PAYLOAD를 검증하세요.
    pass
except ValidationError as error:
    # TODO: error.errors()를 순회하며 loc와 msg를 출력하세요.
    print(error)
