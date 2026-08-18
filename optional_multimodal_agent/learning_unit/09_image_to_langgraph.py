"""이미지 원본 없이 분석 결과만 LangGraph State에 저장하는 예제."""


state = {
    "message": "부산 여행 계획을 만들어 주세요.",
    "image_analysis": {
        "scene_type": "transport",
        "summary": "부산행 기차 승차권입니다.",
    },
    "trace": [{"node": "use_image_analysis", "status": "completed"}],
}

assert "image_bytes" not in state
assert "image_base64" not in state
print(state)
