"""TODO 5: Schema별 Mock 결과를 검증한 뒤 실제 Provider로 확장하세요."""

from typing import Any

from pydantic import BaseModel

from support_ticket_schema import SupportTicket
from travel_plan_schema import TravelPlan


MOCK_OUTPUTS: dict[str, tuple[type[BaseModel], dict[str, Any]]] = {
    "travel_plan": (
        TravelPlan,
        {
            "destination": "부산",
            "summary": "대표 장소를 둘러보는 교육용 일정",
            "recommended_days": 3,
            "activities": ["지역 명소 방문", "현지 음식 체험"],
            "cautions": ["운영 시간을 확인하세요."],
        },
    ),
    "support_ticket": (
        SupportTicket,
        {
            "category": "billing",
            "priority": "medium",
            "summary": "중복 결제 확인 요청",
            "requires_human": True,
            "missing_information": ["주문 번호"],
        },
    ),
}


for schema_name, (model_class, mock_output) in MOCK_OUTPUTS.items():
    # TODO: mock_output을 model_class로 검증하고 JSON으로 출력하세요.
    print(f"{schema_name}: 검증 코드를 완성하세요.")
