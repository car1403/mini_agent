"""실행 성공과 올바른 동작이 다르다는 것을 확인합니다."""

agent_result = {
    "status": "completed",
    "tool": "search_hotels",
}
expected = {
    "status": "needs_input",
    "tool": None,
}

checks = {
    "status_match": agent_result["status"] == expected["status"],
    "tool_match": agent_result["tool"] == expected["tool"],
}

print("프로그램 실행 성공:", agent_result["status"] == "completed")
print("Agent 행동 평가:", {"passed": all(checks.values()), "checks": checks})
