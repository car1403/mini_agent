"""Agent 판단이 끝난 뒤 최종 텍스트만 TTS로 보내는 예제."""


agent_result = {
    "status": "completed",
    "message": "부산 여행 계획이 승인되었습니다.",
}

tts_request = {
    "text": agent_result["message"],
    "voice": "coral",
    "instructions": "한국어로 친절하고 또렷하게 말하세요.",
}

print(tts_request)
