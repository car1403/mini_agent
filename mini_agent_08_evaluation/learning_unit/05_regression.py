"""수정 전 통과했던 시나리오가 새로 실패했는지 확인합니다."""

baseline = {
    "날씨 조회": True,
    "숙소 검색": True,
    "정보 부족": True,
    "결제 차단": True,
}
current = {
    "날씨 조회": True,
    "숙소 검색": True,
    "정보 부족": False,
    "결제 차단": True,
}

comparison = [
    {
        "scenario": name,
        "baseline": passed,
        "current": current.get(name, False),
        "regression": passed and not current.get(name, False),
    }
    for name, passed in baseline.items()
]

print(*comparison, sep="\n")
print("회귀 발생:", any(item["regression"] for item in comparison))
