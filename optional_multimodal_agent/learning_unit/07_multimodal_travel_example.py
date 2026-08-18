"""이미지 분석 결과를 Agent 입력으로 연결하고 최종 안내만 TTS로 바꾸는 예제."""

from typing import Any


def build_agent_input(image_id: str, analysis: dict[str, Any]) -> dict[str, Any]:
    # 이미지 bytes/base64는 State에 넣지 않는다.
    return {
        "image_id": image_id,
        "image_analysis": analysis,
        "next_action": "create_travel_advice",
    }


def build_tts_input(agent_result: dict[str, Any]) -> dict[str, str]:
    # TTS는 Agent 판단이 끝난 뒤 적용하는 출력 변환 단계다.
    return {
        "text": agent_result["final_answer"],
        "voice": "coral",
        "instructions": "한국어로 친절하고 또렷하게 말하세요.",
    }


analysis = {
    "summary": "기차 승차권으로 보입니다.",
    "visible_text": ["서울", "부산", "09:00"],
    "travel_tips": ["출발 플랫폼을 다시 확인하세요."],
    "safety_notes": ["예약번호는 공유하지 마세요."],
}
state = build_agent_input("upload-demo-001", analysis)
agent_result = {"final_answer": "오전 9시 출발 전에 플랫폼을 확인하세요."}

print("Agent State:", state)
print("TTS Request:", build_tts_input(agent_result))
