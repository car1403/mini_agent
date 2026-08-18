"""State는 Workflow의 함수들이 함께 읽고 쓰는 데이터입니다."""

from typing import TypedDict


class TravelState(TypedDict, total=False):
    message: str
    destination: str
    status: str


if __name__ == "__main__":
    state: TravelState = {"message": "부산으로 여행 가고 싶어요", "status": "started"}
    print("처음 State:", state)
    state["destination"] = "부산"
    print("목적지 추가 후:", state)
