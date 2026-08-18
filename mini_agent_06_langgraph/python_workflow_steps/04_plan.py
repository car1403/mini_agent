def create_plan(state: dict) -> dict:
    return {
        **state,
        "plan": {
            "destination": state["destination"],
            "summary": "대중교통을 이용하는 부산 여행",
        },
    }


print(create_plan({"destination": "부산"}))
