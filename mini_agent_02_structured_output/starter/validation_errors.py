"""TODO 4: 두 Schema의 오류 필드와 메시지를 출력하세요."""

from typing import Any

from pydantic import BaseModel, ValidationError

from support_ticket_schema import SupportTicket
from travel_plan_schema import TravelPlan


SAMPLES: dict[str, tuple[type[BaseModel], dict[str, Any]]] = {
    "travel_plan": (
        TravelPlan,
        {
            "destination": "부산",
            "summary": "대중교통 중심 여행",
            "recommended_days": 0,
            "activities": [],
            "cautions": [],
        },
    ),
    "support_ticket": (
        SupportTicket,
        {
            "category": "refund",
            "priority": "urgent",
            "summary": "환불 요청",
            "requires_human": "yes",
            "missing_information": [],
        },
    ),
}


for schema_name, (model_class, payload) in SAMPLES.items():
    print(f"\n[{schema_name}]")
    try:
        # TODO: model_class.model_validate()로 payload를 검증하세요.
        pass
    except ValidationError as error:
        # TODO: error.errors()를 순회하며 loc와 msg를 출력하세요.
        print(error)
