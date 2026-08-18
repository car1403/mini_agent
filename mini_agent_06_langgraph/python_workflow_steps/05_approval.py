def wait_for_approval(state: dict) -> dict:
    return {
        **state,
        "status": "waiting_approval",
        "requires_approval": True,
    }


print(wait_for_approval({"plan": {"destination": "부산"}}))
