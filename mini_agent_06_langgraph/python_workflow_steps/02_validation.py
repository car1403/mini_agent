def validate_request(state: dict) -> dict:
    missing = []
    if not state.get("destination"):
        missing.append("destination")
    return {**state, "missing_fields": missing}


print(validate_request({"destination": None}))
print(validate_request({"destination": "부산"}))
