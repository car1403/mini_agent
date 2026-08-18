def select_relevant(memories: list[dict], question: str) -> list[dict]:
    """TODO: 음식·교통·숙소 질문에 필요한 Memory만 반환하세요."""
    raise NotImplementedError


if __name__ == "__main__":
    items = [
        {"key": "transportation", "value": "대중교통"},
        {"key": "food_restriction", "value": "해산물 알레르기"},
    ]
    print(select_relevant(items, "식당을 추천해줘"))
