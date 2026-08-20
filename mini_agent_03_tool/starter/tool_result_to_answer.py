def make_final_answer(question: str, tool_result: dict) -> str:
    """TODO: Tool Result의 값만 사용해 사용자용 최종 답변을 만드세요."""
    raise NotImplementedError


if __name__ == "__main__":
    result = {
        "success": True,
        "data": {"city": "부산", "condition": "맑음", "temperature_c": 26},
    }
    print(make_final_answer("부산 날씨를 알려줘", result))
