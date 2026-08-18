"""구조화된 이미지 분석 결과를 Python Agent 입력으로 바꾸는 예제."""


analysis = {
    "scene_type": "transport",
    "summary": "부산행 기차 승차권입니다.",
    "travel_tips": ["출발 시간을 확인하세요."],
    "safety_notes": ["예약번호를 공개하지 마세요."],
}

agent_payload = {
    "user_id": "demo-user",
    "message": "부산 여행 계획을 만들어 주세요.",
    "provider": "mock",
    "image_analysis": analysis,
}

print(agent_payload)
