"""여행 Agent용 표 기반 Mock 평가."""

SCENARIOS = [
    {
        "input": "서울 날씨를 알려줘.",
        "expected_tool": "get_weather",
        "actual_tool": "get_weather",
        "expected_status": "completed",
        "actual_status": "completed",
    },
    {
        "input": "호텔을 지금 결제해줘.",
        "expected_tool": None,
        "actual_tool": None,
        "expected_status": "blocked",
        "actual_status": "blocked",
    },
    {
        "input": "부산 여행을 준비해줘.",
        "expected_tool": None,
        "actual_tool": "search_hotels",
        "expected_status": "needs_input",
        "actual_status": "completed",
    },
]


def evaluate(item: dict) -> dict:
    tool_match = item["expected_tool"] == item["actual_tool"]
    status_match = item["expected_status"] == item["actual_status"]
    return {
        "input": item["input"],
        "passed": tool_match and status_match,
        "tool_match": tool_match,
        "status_match": status_match,
    }


if __name__ == "__main__":
    results = [evaluate(item) for item in SCENARIOS]
    for result in results:
        print(result)
    print("통과율:", sum(item["passed"] for item in results) / len(results))
