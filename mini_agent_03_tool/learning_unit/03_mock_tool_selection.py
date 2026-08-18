"""사용자 문장에서 Tool을 선택하지만 아직 실행하지 않습니다."""


def select_tool(message: str) -> dict:
    if any(word in message for word in ("날씨", "기온", "우산", "비예보")):
        return {"tool_name": "get_weather", "reason": "날씨 관련 요청", "confidence": 0.92}
    if any(word in message for word in ("호텔", "숙소", "체크인")):
        return {"tool_name": "search_hotels", "reason": "숙소 관련 요청", "confidence": 0.94}
    if any(word in message for word in ("관광지", "가볼", "명소")):
        return {"tool_name": "search_attractions", "reason": "관광지 관련 요청", "confidence": 0.9}
    return {"tool_name": None, "reason": "필요한 Tool을 확정할 수 없음", "confidence": 0.35}


if __name__ == "__main__":
    messages = [
        "부산 날씨를 알려줘",
        "제주 숙소를 찾아줘",
        "서울 관광지를 추천해줘",
        "여행을 준비하고 있어요",
    ]
    for message in messages:
        print(message, "→", select_tool(message))

    print("\n중요: 위 결과는 실행 명령이 아니라 Tool Call 제안입니다.")
