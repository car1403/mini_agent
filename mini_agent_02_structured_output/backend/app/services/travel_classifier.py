def classify_travel_request(message: str) -> dict:
    normalized = message.strip()
    if any(word in normalized for word in ("날씨", "기온", "우산", "비가", "비예보")):
        result = ("weather", "날씨 관련 표현을 찾았습니다.", 0.92, [])
    elif any(word in normalized for word in ("호텔", "숙소", "예약", "취소")):
        result = ("accommodation", "숙박 관련 표현을 찾았습니다.", 0.88, [])
    elif any(word in normalized for word in ("여행", "일정", "코스")):
        missing = [] if any(city in normalized for city in ("서울", "부산", "제주", "강릉")) else ["destination"]
        result = ("travel_plan", "여행 계획 표현을 찾았습니다.", 0.84 if not missing else 0.62, missing)
    else:
        result = ("needs_clarification", "요청을 판단할 정보가 부족합니다.", 0.3, ["request"])

    intent, reason, confidence, missing_information = result
    ask_user = confidence < 0.7 or bool(missing_information)
    if "destination" in missing_information:
        question = "어느 지역으로 여행하고 싶으신가요?"
    elif ask_user:
        question = "여행 계획, 숙소, 날씨 중 어떤 도움이 필요한가요?"
    else:
        question = ""
    return {
        "intent": intent,
        "reason": reason,
        "confidence": confidence,
        "missing_information": missing_information,
        "next_action": "ask_user" if ask_user else "continue",
        "follow_up_question": question,
    }
