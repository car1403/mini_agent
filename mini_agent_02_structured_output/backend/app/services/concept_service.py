def fixed_workflow(message: str) -> dict:
    return {
        "route": "travel_plan",
        "reason": "입력 내용과 관계없이 미리 정한 단계로 이동합니다.",
        "confidence": 1.0,
    }


def mock_semantic_router(message: str) -> dict:
    normalized = message.strip()
    if any(word in normalized for word in ("날씨", "기온", "우산", "비가", "비예보")):
        return {"route": "weather", "reason": "날씨 표현을 찾았습니다.", "confidence": 0.92}
    if any(word in normalized for word in ("호텔", "숙소", "예약")):
        return {"route": "accommodation", "reason": "숙박 표현을 찾았습니다.", "confidence": 0.88}
    if any(word in normalized for word in ("여행", "일정", "코스")):
        return {"route": "travel_plan", "reason": "여행 계획 표현을 찾았습니다.", "confidence": 0.84}
    return {"route": "needs_clarification", "reason": "의도를 판단할 정보가 부족합니다.", "confidence": 0.35}


def compare_decisions(message: str) -> dict:
    return {
        "message": message,
        "workflow": fixed_workflow(message),
        "semantic_router": mock_semantic_router(message),
        "note": "Router의 판단만으로는 Agent가 아닙니다. Tool 실행, 결과 관찰, 종료 판단이 추가되어야 합니다.",
    }
