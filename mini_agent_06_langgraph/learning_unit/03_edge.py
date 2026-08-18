"""Edge는 Node의 실행 순서를 연결합니다. 아직 LangGraph를 사용하지 않습니다."""


def extract(state: dict) -> dict:
    return {**state, "destination": "부산" if "부산" in state["message"] else None}


def make_answer(state: dict) -> dict:
    destination = state.get("destination") or "목적지 미정"
    return {**state, "answer": f"{destination} 여행 요청을 확인했습니다."}


EDGES = ["START → extract", "extract → make_answer", "make_answer → END"]


if __name__ == "__main__":
    print("실행 순서:", " | ".join(EDGES))
    state = {"message": "부산 여행을 준비해줘"}
    state = extract(state)
    state = make_answer(state)
    print("최종 State:", state)
