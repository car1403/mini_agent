"""Node는 State를 받고 변경할 값만 dict로 반환하는 함수입니다."""

from typing import TypedDict


class TravelState(TypedDict, total=False):
    message: str
    destination: str | None
    status: str


def extract_destination(state: TravelState) -> dict:
    destination = "부산" if "부산" in state["message"] else None
    return {"destination": destination}


if __name__ == "__main__":
    state: TravelState = {"message": "부산으로 여행 가고 싶어요", "status": "started"}
    update = extract_destination(state)
    print("Node 입력:", state)
    print("Node가 반환한 변경값:", update)
    print("변경값을 합친 State:", {**state, **update})
