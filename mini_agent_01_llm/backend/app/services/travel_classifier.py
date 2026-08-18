"""여행 문의 분류와 안전한 다음 행동을 결정하는 순수 함수."""


def classify_travel_request(message: str) -> dict:
    text = message.replace(" ", "")
    if any(word in text for word in ("취소", "환불", "수수료")):
        result = {
            "intent": "policy",
            "reason": "취소·환불 관련 표현",
            "confidence": 0.94,
            "missing_information": [],
        }
    elif any(word in text for word in ("날씨", "비가", "비예보", "기온", "우산")):
        result = {
            "intent": "weather",
            "reason": "날씨 관련 표현",
            "confidence": 0.9,
            "missing_information": [],
        }
    elif any(word in text for word in ("호텔", "숙소", "체크인")):
        result = {
            "intent": "accommodation",
            "reason": "숙소 관련 표현",
            "confidence": 0.92,
            "missing_information": [],
        }
    elif any(word in text for word in ("일정", "여행", "코스")):
        missing = [] if any(city in text for city in ("서울", "부산", "제주", "강릉")) else ["destination"]
        result = {
            "intent": "travel_plan",
            "reason": "여행 일정 관련 표현",
            "confidence": 0.87,
            "missing_information": missing,
        }
    else:
        result = {
            "intent": "needs_clarification",
            "reason": "분류 근거가 부족함",
            "confidence": 0.35,
            "missing_information": ["request_detail"],
        }
    return {**result, **decide_next_action(result)}


def decide_next_action(result: dict) -> dict[str, str]:
    if result["confidence"] < 0.6:
        return {
            "next_action": "ask_user",
            "follow_up_question": "어떤 도움을 원하는지 조금 더 구체적으로 알려주세요.",
        }
    if "destination" in result["missing_information"]:
        return {
            "next_action": "ask_user",
            "follow_up_question": "어느 지역으로 여행하고 싶은가요?",
        }
    return {"next_action": "continue", "follow_up_question": ""}
