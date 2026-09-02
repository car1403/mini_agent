def extract_request(message: str) -> dict:
    return {
        "message": message,
        "destination": "부산" if "부산" in message else None,
    }


state = extract_request("부산 여행을 가고 싶어요.")
print(state)
