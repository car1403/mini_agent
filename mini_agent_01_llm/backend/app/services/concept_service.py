"""LLM, Workflow, Agent의 차이를 화면에서 비교하기 위한 순수 함수."""


def fixed_workflow(message: str) -> dict:
    if "날씨" in message:
        return {"route": "weather", "reason": "날씨 키워드 규칙", "confidence": 1.0}
    if "취소" in message or "환불" in message:
        return {"route": "policy", "reason": "취소·환불 키워드 규칙", "confidence": 1.0}
    return {"route": "general", "reason": "일치하는 고정 규칙 없음", "confidence": 0.5}


def mock_semantic_router(message: str) -> dict:
    normalized = message.replace(" ", "")
    if any(word in normalized for word in ("비가올", "우산", "기온")):
        return {"route": "weather", "reason": "날씨와 관련된 의미를 감지", "confidence": 0.85}
    if any(word in normalized for word in ("돌려받", "취소수수료")):
        return {"route": "policy", "reason": "취소·환불 의도를 감지", "confidence": 0.88}
    return {
        "route": "needs_clarification",
        "reason": "업무 유형을 확정하기 어려움",
        "confidence": 0.4,
    }


def compare_decisions(message: str) -> dict:
    return {
        "message": message,
        "workflow": fixed_workflow(message),
        "semantic_router": mock_semantic_router(message),
        "note": (
            "의미 기반 Mock Router는 LLM 판단을 흉내 내는 중간 예제입니다. "
            "완성된 Agent는 이후 Tool 실행, 결과 관찰, 종료 결정까지 포함합니다."
        ),
    }
