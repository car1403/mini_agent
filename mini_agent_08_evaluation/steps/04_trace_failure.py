"""Trace에서 처음 실패한 단계를 찾습니다."""

trace = [
    {"node": "extract_request", "status": "completed", "duration_ms": 12},
    {
        "node": "select_tool",
        "tool": "search_hotels",
        "status": "completed",
        "duration_ms": 8,
    },
    {
        "node": "run_tool",
        "tool": "search_hotels",
        "status": "failed",
        "duration_ms": 1000,
        "error": "timeout",
    },
]

failed = next((event for event in trace if event["status"] == "failed"), None)
print("전체 Trace:", trace)
print("첫 실패:", failed)
