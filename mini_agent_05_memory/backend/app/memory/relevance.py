from app.schemas import MemoryItem


def relevant_memories(items: list[MemoryItem], question: str) -> list[MemoryItem]:
    keys = set()
    if any(word in question for word in ("이동", "교통", "경로")):
        keys.add("transportation")
    if any(word in question for word in ("음식", "식당", "먹")):
        keys.add("food_restriction")
    if any(word in question for word in ("호텔", "숙소")):
        keys.add("hotel_preference")
    return [item for item in items if item.key in keys]
