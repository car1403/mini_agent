"""Ollama Structured Output으로 요청을 7개 Lab 중 하나로 분류하는 Agent입니다."""
from typing import Literal
from pydantic import BaseModel, Field
from app.core.config import settings
from app.providers.registry import get_provider
from app.schemas.lab import LabRouteDecision

class RoutePrediction(BaseModel):
    lab_id: Literal["parking", "air_conditioner", "parcel_locker", "cafe", "library", "inventory", "travel", "unknown"]
    confidence: float = Field(ge=0, le=1)
    reason: str

SYSTEM_PROMPT = """Tool Use 교육용 요청을 정확히 하나로 분류하세요.
parking=차량/주차장 문, air_conditioner=온도/에어컨, parcel_locker=택배함/인증코드,
cafe=커피 주문, library=회원/도서 대출, inventory=SKU/재고 예약,
travel=도시/날짜/날씨/관광지 여행 준비. 판단 불가하면 unknown입니다."""

def classify_lab(message: str) -> LabRouteDecision:
    """Lab을 제안하지만 Handler를 실행하지는 않습니다.

    Routing Service가 confidence와 Allowlist를 검사한 뒤에만 실제 Handler를 호출합니다.
    """
    response = get_provider("ollama").generate_structured(SYSTEM_PROMPT, message, RoutePrediction)
    return LabRouteDecision(**response.content, provider="ollama", model=settings.ollama_model)

def explicit_decision(lab_id: str) -> LabRouteDecision:
    """사용자가 고른 Lab을 LLM 없이 결정적으로 표현해 실습 재현성을 보장합니다."""
    return LabRouteDecision(lab_id=lab_id, confidence=1.0, reason="사용자가 Lab을 명시적으로 선택했습니다.", provider="explicit", model="none")

